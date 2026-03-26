"""create delivery_events table

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mirrors DeliveryEventType in app/models/enums.py
delivery_event_type = sa.Enum(
    "eta_updated", "status_changed", "tracking_stalled",
    "anomaly_detected", "delivered",
    name="deliveryeventtype",
)


def upgrade() -> None:
    delivery_event_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "delivery_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", delivery_event_type, nullable=False),
        sa.Column("previous_eta", sa.Date(), nullable=True),
        sa.Column("new_eta", sa.Date(), nullable=True),
        sa.Column("carrier_status_raw", sa.String(255), nullable=True),
        sa.Column("is_anomaly", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_delivery_events_order_id", "delivery_events", ["order_id"])
    op.create_index("ix_delivery_events_is_anomaly", "delivery_events", ["is_anomaly"])


def downgrade() -> None:
    op.drop_index("ix_delivery_events_is_anomaly", table_name="delivery_events")
    op.drop_index("ix_delivery_events_order_id", table_name="delivery_events")
    op.drop_table("delivery_events")
    delivery_event_type.drop(op.get_bind(), checkfirst=True)
