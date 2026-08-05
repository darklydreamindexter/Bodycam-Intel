import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class CaseStatus(str, enum.Enum):
    DISCOVERED = "discovered"
    UNDER_REVIEW = "under_review"
    CONSOLIDATED = "consolidated"
    PRIORITIZED = "prioritized"
    REQUEST_DRAFTED = "request_drafted"
    AWAITING_APPROVAL = "awaiting_approval"
    SUBMITTED = "submitted"
    FULFILLED = "fulfilled"
    PRODUCTION_READY = "production_ready"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class RequestStatus(str, enum.Enum):
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    CLARIFICATION_NEEDED = "clarification_needed"
    FULFILLED = "fulfilled"
    DENIED = "denied"
    CLOSED = "closed"


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    agency_type: Mapped[str] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(120))
    county: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(2), index=True)
    records_email: Mapped[str | None] = mapped_column(String(255))
    records_portal_url: Mapped[str | None] = mapped_column(String(1000))
    phone: Mapped[str | None] = mapped_column(String(40))
    retention_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    cases: Mapped[list["Case"]] = relationship(back_populates="primary_agency")


class CollectionSource(Base):
    """A deliberately opted-in public RSS or official-release source."""

    __tablename__ = "collection_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(40), default="rss")
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    homepage_url: Mapped[str | None] = mapped_column(String(1000))
    default_state: Mapped[str | None] = mapped_column(String(2), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    reliability_score: Mapped[int] = mapped_column(Integer, default=60)
    poll_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_collection_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    collection_lock_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    documents: Mapped[list["SourceDocument"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    runs: Mapped[list["CollectionRun"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    city: Mapped[str | None] = mapped_column(String(120))
    county: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(2), index=True)
    incident_number: Mapped[str | None] = mapped_column(String(120), index=True)
    cad_number: Mapped[str | None] = mapped_column(String(120), index=True)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.DISCOVERED, index=True)
    confidence: Mapped[int] = mapped_column(Integer, default=0)
    primary_agency_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agencies.id"))
    source_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    primary_agency: Mapped[Agency | None] = relationship(back_populates="cases")
    scorecards: Mapped[list["Scorecard"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    record_requests: Mapped[list["RecordRequest"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    source_documents: Mapped[list["SourceDocument"]] = relationship(back_populates="case")


class SourceDocument(Base):
    """Immutable collection evidence. Full media/file acquisition is intentionally out of scope here."""

    __tablename__ = "source_documents"
    __table_args__ = (UniqueConstraint("source_id", "canonical_url", name="uq_source_documents_source_url"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collection_sources.id"), index=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cases.id"), index=True)
    canonical_url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(500))
    excerpt: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    keyword_hits: Mapped[list[str]] = mapped_column(JSON, default=list)
    metadata_payload: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    source: Mapped[CollectionSource] = relationship(back_populates="documents")
    case: Mapped[Case | None] = relationship(back_populates="source_documents")


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collection_sources.id"), index=True)
    trigger: Mapped[str] = mapped_column(String(40), default="scheduled")
    status: Mapped[str] = mapped_column(String(30), default="running", index=True)
    documents_seen: Mapped[int] = mapped_column(Integer, default=0)
    documents_new: Mapped[int] = mapped_column(Integer, default=0)
    candidate_cases_created: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source: Mapped[CollectionSource] = relationship(back_populates="runs")


class Scorecard(Base):
    __tablename__ = "scorecards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), index=True)
    version: Mapped[str] = mapped_column(String(40), default="v1")
    recording_likelihood: Mapped[int] = mapped_column(Integer)
    editorial_value: Mapped[int] = mapped_column(Integer)
    acquisition_feasibility: Mapped[int] = mapped_column(Integer)
    legal_risk: Mapped[int] = mapped_column(Integer)
    timeliness: Mapped[int] = mapped_column(Integer)
    estimated_cost: Mapped[int] = mapped_column(Integer)
    total_score: Mapped[int] = mapped_column(Integer, index=True)
    explanation: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case: Mapped[Case] = relationship(back_populates="scorecards")


class RecordRequest(Base):
    __tablename__ = "record_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), index=True)
    agency_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agencies.id"), index=True)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.DRAFT, index=True)
    subject: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    requested_items: Mapped[list[str]] = mapped_column(JSON, default=list)
    jurisdiction_notes: Mapped[str | None] = mapped_column(Text)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case: Mapped[Case] = relationship(back_populates="record_requests")


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action: Mapped[str] = mapped_column(String(160), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(255), default="local-owner")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
