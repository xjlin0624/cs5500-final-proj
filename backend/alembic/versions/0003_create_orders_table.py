"""create orders table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-25

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mirrors the OrderStatus enum in app/models/enums.py
order_status = sa.Enum(
    "pending", "shipped", "in_transit", "delivered", "cancelled", "returned",
    name="orderstatus",
)


def upgrade() -> None:
    order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("retailer", sa.String(50), nullable=False),
        sa.Column("retailer_order_id", sa.String(255), nullable=False),
        sa.Column("order_status", order_status, nullable=False),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("return_window_days", sa.Integer(), nullable=True),
        sa.Column("return_deadline", sa.Date(), nullable=True),
        sa.Column(
            "price_match_eligible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("tracking_number", sa.String(100), nullable=True),
        sa.Column("carrier", sa.String(50), nullable=True),
        sa.Column("estimated_delivery", sa.Date(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_url", sa.Text(), nullable=True),
        sa.Column("raw_capture", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id", "retailer", "retailer_order_id",
            name="uq_order_per_user_retailer",
        ),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_order_date", "orders", ["order_date"])


def downgrade() -> None:
    op.drop_index("ix_orders_order_date", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
    order_status.drop(op.get_bind(), checkfirst=True)
