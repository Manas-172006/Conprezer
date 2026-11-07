"""Create user and conversion tables.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "conversions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("input_type", sa.String(length=16), nullable=False),
        sa.Column("output_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("input_url", sa.String(length=512), nullable=False),
        sa.Column("output_url", sa.String(length=512), nullable=True),
        sa.Column("original_size", sa.BigInteger(), nullable=False),
        sa.Column("output_size", sa.BigInteger(), nullable=True),
        sa.Column("ttl", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Index("ix_conversions_user_id", "user_id"),
        sa.Index("ix_conversions_status", "status"),
    )
    op.execute("DELETE FROM conversions WHERE ttl < NOW()")
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False),
        sa.UniqueConstraint("user_id", "key", name="uq_user_preferences_user_key"),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
    op.drop_index("ix_conversions_status", table_name="conversions")
    op.drop_index("ix_conversions_user_id", table_name="conversions")
    op.drop_table("conversions")
    op.drop_table("users")
