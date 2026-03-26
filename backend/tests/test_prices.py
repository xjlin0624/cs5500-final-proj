"""
Unit tests for GET /api/prices/{item_id}/history (FR-6 top-level endpoint).
Uses the FakeSession pattern — no real database required.
"""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.deps import get_current_user, get_db
from backend.app.main import app
from backend.app.models.enums import SnapshotSource
from backend.app.models.order_item import OrderItem
from backend.app.models.price_snapshot import PriceSnapshot
from backend.app.models.user import User


# ---------------------------------------------------------------------------
# Fake session
# ---------------------------------------------------------------------------

class FakePricesSession:
    def __init__(self, item: OrderItem | None, snapshots: list[PriceSnapshot] | None = None):
        self._item = item
        self._snapshots = snapshots or []

    def get(self, model, pk):
        if model is OrderItem:
            return self._item if self._item and str(self._item.id) == str(pk) else None
        return None

    def query(self, model):
        if model is PriceSnapshot:
            return _FakeSnapshotQuery(self._snapshots)
        return _FakeSnapshotQuery([])


class _FakeSnapshotQuery:
    def __init__(self, snapshots):
        self._snapshots = list(snapshots)

    def filter(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def limit(self, n):
        self._snapshots = self._snapshots[:n]
        return self

    def all(self):
        return self._snapshots


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user() -> User:
    return User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hash",
        is_active=True,
        is_verified=False,
    )


def _make_item(user: User) -> OrderItem:
    return OrderItem(
        id=uuid4(),
        order_id=uuid4(),
        user_id=user.id,
        product_name="Widget",
        product_url="https://example.com/item",
        paid_price=99.99,
        is_monitoring_active=True,
    )


def _make_snapshot(item: OrderItem, scraped_price: float = 79.99) -> PriceSnapshot:
    return PriceSnapshot(
        id=uuid4(),
        order_item_id=item.id,
        scraped_price=scraped_price,
        original_paid_price=item.paid_price,
        currency="USD",
        is_available=True,
        snapshot_source=SnapshotSource.scheduled_job,
        scraped_at=datetime.now(timezone.utc),
    )


def _make_client(session: FakePricesSession, user: User) -> TestClient:
    app.dependency_overrides[get_db] = lambda: (yield session)
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_price_history_returns_snapshots():
    user = _make_user()
    item = _make_item(user)
    snapshots = [_make_snapshot(item, 79.99), _make_snapshot(item, 85.00)]
    client = _make_client(FakePricesSession(item, snapshots), user)

    resp = client.get(f"/api/prices/{item.id}/history")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["scraped_price"] == 79.99


def test_get_price_history_empty_returns_empty_list():
    user = _make_user()
    item = _make_item(user)
    client = _make_client(FakePricesSession(item, []), user)

    resp = client.get(f"/api/prices/{item.id}/history")

    assert resp.status_code == 200
    assert resp.json() == []


def test_get_price_history_unknown_item_returns_404():
    user = _make_user()
    client = _make_client(FakePricesSession(None), user)

    resp = client.get(f"/api/prices/{uuid4()}/history")

    assert resp.status_code == 404


def test_get_price_history_other_users_item_returns_404():
    user = _make_user()
    other_user = _make_user()
    item = _make_item(other_user)  # owned by other_user
    client = _make_client(FakePricesSession(item), user)

    resp = client.get(f"/api/prices/{item.id}/history")

    assert resp.status_code == 404


def test_get_price_history_limit_is_respected():
    user = _make_user()
    item = _make_item(user)
    snapshots = [_make_snapshot(item, float(i)) for i in range(10)]
    client = _make_client(FakePricesSession(item, snapshots), user)

    resp = client.get(f"/api/prices/{item.id}/history?limit=3")

    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_price_history_includes_price_delta():
    user = _make_user()
    item = _make_item(user)  # paid_price=99.99
    snap = _make_snapshot(item, scraped_price=79.99)
    client = _make_client(FakePricesSession(item, [snap]), user)

    resp = client.get(f"/api/prices/{item.id}/history")

    assert resp.status_code == 200
    assert resp.json()[0]["price_delta"] == 20.0
