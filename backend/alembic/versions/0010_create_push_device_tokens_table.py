"""create push_device_tokens table

Revision ID: 0010
Revises: 0009
Create Date: 2026-04-14

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "push_device_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False, server_default=sa.text("'web'")),
        sa.Column("browser", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
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
        sa.UniqueConstraint("token", name="uq_push_device_tokens_token"),
    )
    op.create_index("ix_push_device_tokens_user_id", "push_device_tokens", ["user_id"])
    op.create_index("ix_push_device_tokens_active", "push_device_tokens", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_push_device_tokens_active", table_name="push_device_tokens")
    op.drop_index("ix_push_device_tokens_user_id", table_name="push_device_tokens")
    op.drop_table("push_device_tokens")
