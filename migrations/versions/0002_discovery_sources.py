"""discovery sources and source evidence

Revision ID: 0002_discovery_sources
Revises: 0001_initial_foundation
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_discovery_sources"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collection_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("homepage_url", sa.String(1000)),
        sa.Column("default_state", sa.String(2)),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("reliability_score", sa.Integer(), nullable=False),
        sa.Column("poll_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("last_collected_at", sa.DateTime(timezone=True)),
        sa.Column("next_collection_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_collection_sources_name", "collection_sources", ["name"], unique=True)
    op.create_index("uq_collection_sources_url", "collection_sources", ["url"], unique=True)
    op.create_index("ix_collection_sources_default_state", "collection_sources", ["default_state"])
    op.create_index("ix_collection_sources_active", "collection_sources", ["active"])
    op.create_index("ix_collection_sources_next_collection_at", "collection_sources", ["next_collection_at"])

    op.create_table(
        "collection_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("collection_sources.id"), nullable=False),
        sa.Column("trigger", sa.String(40), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("documents_seen", sa.Integer(), nullable=False),
        sa.Column("documents_new", sa.Integer(), nullable=False),
        sa.Column("candidate_cases_created", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_collection_runs_source_id", "collection_runs", ["source_id"])
    op.create_index("ix_collection_runs_status", "collection_runs", ["status"])

    op.create_table(
        "source_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("collection_sources.id"), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id")),
        sa.Column("canonical_url", sa.String(1000), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("excerpt", sa.Text()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("keyword_hits", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_source_documents_source_id", "source_documents", ["source_id"])
    op.create_index("ix_source_documents_case_id", "source_documents", ["case_id"])
    op.create_index("ix_source_documents_canonical_url", "source_documents", ["canonical_url"])
    op.create_index("uq_source_documents_source_url", "source_documents", ["source_id", "canonical_url"], unique=True)
    op.create_index("ix_source_documents_published_at", "source_documents", ["published_at"])


def downgrade() -> None:
    op.drop_table("source_documents")
    op.drop_table("collection_runs")
    op.drop_table("collection_sources")
