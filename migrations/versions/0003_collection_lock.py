"""prevent concurrent collection of the same source

Revision ID: 0003_collection_lock
Revises: 0002_discovery_sources
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_collection_lock"
down_revision = "0002_discovery_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collection_sources", sa.Column("collection_lock_until", sa.DateTime(timezone=True)))
    op.create_index("ix_collection_sources_collection_lock_until", "collection_sources", ["collection_lock_until"])


def downgrade() -> None:
    op.drop_index("ix_collection_sources_collection_lock_until", table_name="collection_sources")
    op.drop_column("collection_sources", "collection_lock_until")
