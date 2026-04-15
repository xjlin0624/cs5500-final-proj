"""create subscriptions table

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-14

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, ENUM as PgEnum, UUID

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

subscription_status = PgEnum(
    "active", "handled", "cancelled", "monitoring",
    name="subscriptionstatus",
    create_type=False,
)

detection_method = PgEnum(
    "order_pattern", "explicit_subscription_page",
    name="detectionmethod",
    create_type=False,
)


def upgrade() -> None:
    op.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE subscriptionstatus AS ENUM (
                'active', 'handled', 'cancelled', 'monitoring'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """))
    op.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE detectionmethod AS ENUM (
                'order_pattern', 'explicit_subscription_page'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """))

    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("retailer", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=500), nullable=False),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("detection_method", detection_method, nullable=False),
        sa.Column("recurrence_interval_days", sa.Integer(), nullable=True),
        sa.Column("estimated_monthly_cost", sa.Float(), nullable=True),
        sa.Column("last_charged_at", sa.Date(), nullable=True),
        sa.Column("next_expected_charge", sa.Date(), nullable=True),
        sa.Column(
            "status",
            subscription_status,
            nullable=False,
            server_default=sa.text("'monitoring'"),
        ),
        sa.Column("cancellation_url", sa.Text(), nullable=True),
        sa.Column("cancellation_steps", sa.Text(), nullable=True),
        sa.Column("source_order_ids", ARRAY(UUID(as_uuid=True)), nullable=True),
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
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.execute(sa.text("DROP TYPE IF EXISTS detectionmethod"))
    op.execute(sa.text("DROP TYPE IF EXISTS subscriptionstatus"))
