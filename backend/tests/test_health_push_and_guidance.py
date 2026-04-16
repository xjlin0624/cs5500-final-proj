from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_current_user, get_db
from backend.app.main import app
from backend.app.models.push_device_token import PushDeviceToken
from backend.app.models.user import User


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


class _ExecuteResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakePushSession:
    def __init__(self, execute_results=None):
        self.execute_results = list(execute_results or [])
        self.added = []
        self.committed = False

    def execute(self, _stmt):
        value = self.execute_results.pop(0) if self.execute_results else None
        return _ExecuteResult(value)

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        if not getattr(obj, "id", None):
            obj.id = uuid4()
        if not getattr(obj, "last_seen_at", None):
            obj.last_seen_at = datetime.now(timezone.utc)


def _make_user() -> User:
    now = datetime.now(timezone.utc)
    return User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hash",
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )


def _make_client(session, user) -> TestClient:
    app.dependency_overrides[get_db] = lambda: (yield session)
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_returns_ok_when_dependencies_are_healthy(monkeypatch):
    class HealthyDB:
        def execute(self, _stmt):
            return 1

    monkeypatch.setattr("backend.app.api.health.ping_redis", lambda: True)
    app.dependency_overrides[get_db] = lambda: HealthyDB()
    client = TestClient(app)

    response = client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json()["dependencies"] == {"database": True, "redis": True}


def test_register_push_token_creates_token():
    user = _make_user()
    session = FakePushSession(execute_results=[None])
    client = _make_client(session, user)

    response = client.post(
        "/api/push/tokens",
        json={"token": "abc123", "platform": "web", "browser": "Chrome"},
    )

    assert response.status_code == 201
    assert session.committed is True
    assert len(session.added) == 1
    assert session.added[0].token == "abc123"


def test_unregister_push_token_marks_token_inactive():
    user = _make_user()
    token = PushDeviceToken(
        id=uuid4(),
        user_id=user.id,
        token="abc123",
        platform="web",
        browser="Chrome",
        is_active=True,
        last_seen_at=datetime.now(timezone.utc),
    )
    session = FakePushSession(execute_results=[token])
    client = _make_client(session, user)

    response = client.delete("/api/push/tokens/abc123")

    assert response.status_code == 204
    assert token.is_active is False
    assert session.committed is True
