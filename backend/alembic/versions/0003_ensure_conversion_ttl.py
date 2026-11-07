"""Ensure conversions have a TTL column on existing installations.

Revision ID: 0003
Revises: 0002
"""
from alembic import context, op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if context.is_offline_mode():
        return

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("conversions")}
    if "ttl" not in columns:
        op.add_column("conversions", sa.Column("ttl", sa.TIMESTAMP(), nullable=True))
    if "expires_at" in columns:
        op.execute(
            "UPDATE conversions SET ttl = expires_at "
            "WHERE ttl IS NULL AND expires_at IS NOT NULL"
        )

    indexes = {index["name"] for index in inspector.get_indexes("conversions")}
    if "ix_conversions_ttl" not in indexes:
        op.create_index("ix_conversions_ttl", "conversions", ["ttl"])


def downgrade() -> None:
    # TTL is part of the base schema in revision 0001.
    pass
