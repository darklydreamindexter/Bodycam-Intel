"""initial foundation

Revision ID: 0001_initial_foundation
Revises:
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None

case_status = postgresql.ENUM("DISCOVERED", "UNDER_REVIEW", "CONSOLIDATED", "PRIORITIZED", "REQUEST_DRAFTED", "AWAITING_APPROVAL", "SUBMITTED", "FULFILLED", "PRODUCTION_READY", "REJECTED", "DEFERRED", name="casestatus", create_type=False)
request_status = postgresql.ENUM("DRAFT", "AWAITING_APPROVAL", "APPROVED", "SUBMITTED", "CLARIFICATION_NEEDED", "FULFILLED", "DENIED", "CLOSED", name="requeststatus", create_type=False)


def upgrade() -> None:
    case_status.create(op.get_bind(), checkfirst=True)
    request_status.create(op.get_bind(), checkfirst=True)
    op.create_table("agencies", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(255), nullable=False), sa.Column("agency_type", sa.String(80), nullable=False), sa.Column("city", sa.String(120)), sa.Column("county", sa.String(120)), sa.Column("state", sa.String(2), nullable=False), sa.Column("records_email", sa.String(255)), sa.Column("records_portal_url", sa.String(1000)), sa.Column("phone", sa.String(40)), sa.Column("retention_notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_agencies_name", "agencies", ["name"], unique=True)
    op.create_index("ix_agencies_state", "agencies", ["state"])
    op.create_table("cases", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("title", sa.String(500), nullable=False), sa.Column("summary", sa.Text()), sa.Column("occurred_at", sa.DateTime(timezone=True)), sa.Column("city", sa.String(120)), sa.Column("county", sa.String(120)), sa.Column("state", sa.String(2), nullable=False), sa.Column("incident_number", sa.String(120)), sa.Column("cad_number", sa.String(120)), sa.Column("status", case_status, nullable=False), sa.Column("confidence", sa.Integer(), nullable=False), sa.Column("primary_agency_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agencies.id")), sa.Column("source_urls", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    for field in ("title", "occurred_at", "state", "incident_number", "cad_number", "status"):
        op.create_index(f"ix_cases_{field}", "cases", [field])
    op.create_table("scorecards", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False), sa.Column("version", sa.String(40), nullable=False), sa.Column("recording_likelihood", sa.Integer(), nullable=False), sa.Column("editorial_value", sa.Integer(), nullable=False), sa.Column("acquisition_feasibility", sa.Integer(), nullable=False), sa.Column("legal_risk", sa.Integer(), nullable=False), sa.Column("timeliness", sa.Integer(), nullable=False), sa.Column("estimated_cost", sa.Integer(), nullable=False), sa.Column("total_score", sa.Integer(), nullable=False), sa.Column("explanation", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_scorecards_case_id", "scorecards", ["case_id"])
    op.create_index("ix_scorecards_total_score", "scorecards", ["total_score"])
    op.create_table("record_requests", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id"), nullable=False), sa.Column("agency_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agencies.id"), nullable=False), sa.Column("status", request_status, nullable=False), sa.Column("subject", sa.String(500), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("requested_items", sa.JSON(), nullable=False), sa.Column("jurisdiction_notes", sa.Text()), sa.Column("due_at", sa.DateTime(timezone=True)), sa.Column("approved_at", sa.DateTime(timezone=True)), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_record_requests_case_id", "record_requests", ["case_id"])
    op.create_index("ix_record_requests_agency_id", "record_requests", ["agency_id"])
    op.create_index("ix_record_requests_status", "record_requests", ["status"])
    op.create_table("outbox_events", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("topic", sa.String(160), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("processed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_outbox_events_topic", "outbox_events", ["topic"])
    op.create_table("audit_events", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("action", sa.String(160), nullable=False), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.String(80), nullable=False), sa.Column("actor", sa.String(255), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    for field in ("action", "entity_type", "entity_id"):
        op.create_index(f"ix_audit_events_{field}", "audit_events", [field])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("outbox_events")
    op.drop_table("record_requests")
    op.drop_table("scorecards")
    op.drop_table("cases")
    op.drop_table("agencies")
    request_status.drop(op.get_bind(), checkfirst=True)
    case_status.drop(op.get_bind(), checkfirst=True)
