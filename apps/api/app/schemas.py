from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models import CaseStatus, RequestStatus


class CollectionSourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    kind: Literal["rss", "official_rss"] = "rss"
    url: str = Field(min_length=10, max_length=1000)
    homepage_url: str | None = None
    default_state: str | None = Field(default=None, min_length=2, max_length=2)
    reliability_score: int = Field(default=60, ge=0, le=100)
    poll_interval_minutes: int = Field(default=60, ge=15, le=1440)


class CollectionSourceRead(CollectionSourceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    active: bool
    last_collected_at: datetime | None
    next_collection_at: datetime | None
    created_at: datetime


class CollectionRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_id: UUID
    trigger: str
    status: str
    documents_seen: int
    documents_new: int
    candidate_cases_created: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


class AgencyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    agency_type: str
    state: str = Field(min_length=2, max_length=2)
    city: str | None = None
    county: str | None = None
    records_email: str | None = None
    records_portal_url: str | None = None
    phone: str | None = None
    retention_notes: str | None = None


class AgencyRead(AgencyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime


class CaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    state: str = Field(min_length=2, max_length=2)
    summary: str | None = None
    occurred_at: datetime | None = None
    city: str | None = None
    county: str | None = None
    incident_number: str | None = None
    cad_number: str | None = None
    primary_agency_id: UUID | None = None
    source_urls: list[str] = Field(default_factory=list)
    confidence: int = Field(default=0, ge=0, le=100)


class CaseRead(CaseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: CaseStatus
    created_at: datetime


class ScorecardCreate(BaseModel):
    recording_likelihood: int = Field(ge=0, le=100)
    editorial_value: int = Field(ge=0, le=100)
    acquisition_feasibility: int = Field(ge=0, le=100)
    legal_risk: int = Field(ge=0, le=100)
    timeliness: int = Field(ge=0, le=100)
    estimated_cost: int = Field(ge=0, le=100)
    explanation: dict = Field(default_factory=dict)


class ScorecardRead(ScorecardCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    total_score: int
    version: str
    created_at: datetime


class RecordRequestCreate(BaseModel):
    case_id: UUID
    agency_id: UUID
    subject: str
    body: str
    requested_items: list[str] = Field(min_length=1)
    jurisdiction_notes: str | None = None
    due_at: datetime | None = None


class RecordRequestRead(RecordRequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: RequestStatus
    approved_at: datetime | None
    submitted_at: datetime | None
    created_at: datetime


class DashboardSummary(BaseModel):
    cases_total: int
    cases_prioritized: int
    agencies_total: int
    requests_draft: int
    requests_awaiting_approval: int
    requests_submitted: int
    sources_total: int
    collection_runs_failed: int
