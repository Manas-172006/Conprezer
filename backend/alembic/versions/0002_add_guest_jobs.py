"""Add anonymous conversion ownership and expiration.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "conversions",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.add_column("conversions", sa.Column("anon_id", sa.String(length=64), nullable=True))
    op.add_column("conversions", sa.Column("expires_at", sa.DateTime(), nullable=True))
    op.create_index("ix_conversions_anon_id", "conversions", ["anon_id"])


def downgrade() -> None:
    op.execute("DELETE FROM conversions WHERE user_id IS NULL")
    op.drop_index("ix_conversions_anon_id", table_name="conversions")
    op.drop_column("conversions", "expires_at")
    op.drop_column("conversions", "anon_id")
    op.alter_column(
        "conversions",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
