import logging
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Agency, AuditEvent, Case, CaseStatus, CollectionRun, CollectionSource, OutboxEvent, RecordRequest, RequestStatus, Scorecard, SourceDocument
from app.schemas import CaseCreate, CollectionSourceCreate, RecordRequestCreate, ScorecardCreate

logger = logging.getLogger(__name__)

DISCOVERY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "pursuit": ("pursuit", "police chase", "vehicle chase"),
    "dui": ("dui", "dwi", "driving under the influence", "impaired driving"),
    "felony_stop": ("felony stop",),
    "narcotics": ("narcotics", "drug bust", "drug trafficking", "controlled substance"),
    "swat": ("swat", "tactical team", "special weapons"),
    "k9": ("k-9", "k9", "canine unit", "police dog"),
    "robbery": ("robbery", "armed robbery", "carjacking"),
    "homicide": ("homicide", "murder", "fatal shooting"),
    "officer_involved_shooting": ("officer-involved shooting", "officer involved shooting", "police shooting"),
    "arrest": ("arrested", "arrest", "taken into custody"),
}


def _record_event(db: Session, topic: str, entity_type: str, entity_id: UUID, action: str, payload: dict | None = None) -> None:
    safe_payload = payload or {}
    db.add(OutboxEvent(topic=topic, payload={"entity_id": str(entity_id), **safe_payload}))
    db.add(AuditEvent(action=action, entity_type=entity_type, entity_id=str(entity_id), payload=safe_payload))


def create_case(db: Session, data: CaseCreate) -> Case:
    case = Case(**data.model_dump())
    db.add(case)
    db.flush()
    _record_event(db, "case.discovered", "case", case.id, "case.created", {"title": case.title})
    db.commit()
    db.refresh(case)
    return case


def create_collection_source(db: Session, data: CollectionSourceCreate) -> CollectionSource:
    values = data.model_dump()
    values["default_state"] = values["default_state"].upper() if values["default_state"] else None
    source = CollectionSource(**values, next_collection_at=datetime.now(timezone.utc))
    db.add(source)
    db.flush()
    _record_event(db, "source.registered", "collection_source", source.id, "source.created", {"url": source.url, "kind": source.kind})
    db.commit()
    db.refresh(source)
    return source


def schedule_due_sources(db: Session) -> list[str]:
    """Reserve next execution before queueing, preventing notification/task floods."""
    now = datetime.now(timezone.utc)
    due = list(db.scalars(select(CollectionSource).where(
        CollectionSource.active.is_(True),
        CollectionSource.next_collection_at.is_not(None),
        CollectionSource.next_collection_at <= now,
        (CollectionSource.collection_lock_until.is_(None)) | (CollectionSource.collection_lock_until <= now),
    )))
    for source in due:
        source.next_collection_at = now + timedelta(minutes=source.poll_interval_minutes)
        source.collection_lock_until = now + timedelta(minutes=10)
    db.commit()
    return [str(source.id) for source in due]


def reserve_manual_collection(db: Session, source: CollectionSource) -> bool:
    now = datetime.now(timezone.utc)
    if source.collection_lock_until and source.collection_lock_until > now:
        return False
    source.collection_lock_until = now + timedelta(minutes=10)
    source.next_collection_at = now + timedelta(minutes=source.poll_interval_minutes)
    db.commit()
    return True


def _clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)).strip()


def _entry_datetime(entry: object) -> datetime | None:
    raw = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not raw:
        return None
    return datetime(*raw[:6], tzinfo=timezone.utc)


def detect_discovery_keywords(title: str, excerpt: str) -> list[str]:
    haystack = f"{title} {excerpt}".lower()
    return [label for label, phrases in DISCOVERY_KEYWORDS.items() if any(phrase in haystack for phrase in phrases)]


def collect_rss_source(db: Session, source_id: UUID, trigger: str = "scheduled") -> CollectionRun:
    """Collect a source once, preserving every feed item before deriving candidate cases."""
    source = db.get(CollectionSource, source_id)
    if not source:
        raise ValueError("Collection source not found.")
    if not source.active:
        raise ValueError("Collection source is disabled.")

    run = CollectionRun(source_id=source.id, trigger=trigger, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        response = httpx.get(
            source.url,
            headers={"User-Agent": get_settings().collection_user_agent, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
            timeout=20.0,
            follow_redirects=True,
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if feed.bozo and not feed.entries:
            raise ValueError(f"The response is not a readable RSS/Atom feed: {feed.bozo_exception}")

        entries = list(feed.entries)[:get_settings().collection_max_entries]
        run.documents_seen = len(entries)
        for entry in entries:
            canonical_url = str(getattr(entry, "link", "")).strip()
            title = _clean_text(str(getattr(entry, "title", "Untitled public source")))[:500]
            if not canonical_url:
                continue
            if db.scalar(select(SourceDocument.id).where(SourceDocument.source_id == source.id, SourceDocument.canonical_url == canonical_url)):
                continue

            excerpt = _clean_text(str(getattr(entry, "summary", getattr(entry, "description", ""))))[:5000]
            hits = detect_discovery_keywords(title, excerpt)
            document = SourceDocument(
                source_id=source.id,
                canonical_url=canonical_url[:1000],
                title=title,
                excerpt=excerpt or None,
                published_at=_entry_datetime(entry),
                keyword_hits=hits,
                metadata_payload={"feed_id": str(getattr(entry, "id", ""))[:500]},
            )
            db.add(document)
            run.documents_new += 1

            if hits:
                existing_case_id = db.scalar(select(SourceDocument.case_id).where(
                    SourceDocument.canonical_url == canonical_url,
                    SourceDocument.case_id.is_not(None),
                ))
                if existing_case_id:
                    document.case_id = existing_case_id
                    continue
                confidence = min(95, source.reliability_score + min(20, len(hits) * 5))
                candidate = Case(
                    title=title,
                    summary=excerpt or "Candidate generated from a public feed item; review the linked evidence.",
                    occurred_at=document.published_at,
                    state=source.default_state or "US",
                    status=CaseStatus.DISCOVERED,
                    confidence=confidence,
                    source_urls=[canonical_url],
                )
                db.add(candidate)
                db.flush()
                document.case_id = candidate.id
                run.candidate_cases_created += 1
                _record_event(
                    db,
                    "case.discovered_from_source",
                    "case",
                    candidate.id,
                    "case.discovered_from_source",
                    {"source_id": str(source.id), "document_url": canonical_url, "keyword_hits": hits},
                )

        now = datetime.now(timezone.utc)
        source.last_collected_at = now
        source.next_collection_at = now + timedelta(minutes=source.poll_interval_minutes)
        source.collection_lock_until = None
        run.status = "completed"
        run.finished_at = now
        db.commit()
        db.refresh(run)
        return run
    except Exception as exc:
        db.rollback()
        failed_run = db.get(CollectionRun, run.id)
        if failed_run:
            failed_run.status = "failed"
            failed_run.error_message = str(exc)[:2000]
            failed_run.finished_at = datetime.now(timezone.utc)
            failed_source = db.get(CollectionSource, source_id)
            if failed_source:
                failed_source.collection_lock_until = None
            db.commit()
            db.refresh(failed_run)
            logger.warning("Collection failed for source %s: %s", source_id, exc)
            return failed_run
        raise


def create_scorecard(db: Session, case: Case, data: ScorecardCreate) -> Scorecard:
    values = data.model_dump()
    total = round(
        values["recording_likelihood"] * 0.28
        + values["editorial_value"] * 0.27
        + values["acquisition_feasibility"] * 0.18
        + values["timeliness"] * 0.17
        - values["legal_risk"] * 0.07
        - values["estimated_cost"] * 0.03
    )
    scorecard = Scorecard(case_id=case.id, total_score=max(0, total), **values)
    if scorecard.total_score >= 60 and case.status in {CaseStatus.DISCOVERED, CaseStatus.CONSOLIDATED}:
        case.status = CaseStatus.PRIORITIZED
    db.add(scorecard)
    db.flush()
    _record_event(db, "case.scored", "case", case.id, "case.scorecard_created", {"total_score": scorecard.total_score})
    db.commit()
    db.refresh(scorecard)
    return scorecard


def create_request_draft(db: Session, data: RecordRequestCreate) -> RecordRequest:
    record_request = RecordRequest(**data.model_dump(), status=RequestStatus.DRAFT)
    case = db.get(Case, data.case_id)
    if case and case.status == CaseStatus.PRIORITIZED:
        case.status = CaseStatus.REQUEST_DRAFTED
    db.add(record_request)
    db.flush()
    _record_event(db, "records_request.drafted", "record_request", record_request.id, "record_request.created", {"case_id": str(data.case_id)})
    db.commit()
    db.refresh(record_request)
    return record_request


def request_approval(db: Session, record_request: RecordRequest) -> RecordRequest:
    if record_request.status != RequestStatus.DRAFT:
        raise ValueError("Only draft requests can be sent for approval.")
    record_request.status = RequestStatus.AWAITING_APPROVAL
    case = db.get(Case, record_request.case_id)
    if case:
        case.status = CaseStatus.AWAITING_APPROVAL
    _record_event(db, "records_request.awaiting_approval", "record_request", record_request.id, "record_request.approval_requested")
    db.commit()
    db.refresh(record_request)
    return record_request


def approve_request(db: Session, record_request: RecordRequest) -> RecordRequest:
    if record_request.status != RequestStatus.AWAITING_APPROVAL:
        raise ValueError("Only requests awaiting approval can be approved.")
    record_request.status = RequestStatus.APPROVED
    record_request.approved_at = datetime.now(timezone.utc)
    _record_event(db, "records_request.approved", "record_request", record_request.id, "record_request.approved")
    db.commit()
    db.refresh(record_request)
    return record_request


def dashboard_summary(db: Session) -> dict[str, int]:
    def count(model, condition=None) -> int:
        statement = select(func.count()).select_from(model)
        if condition is not None:
            statement = statement.where(condition)
        return int(db.scalar(statement) or 0)

    return {
        "cases_total": count(Case),
        "cases_prioritized": count(Case, Case.status == CaseStatus.PRIORITIZED),
        "agencies_total": count(Agency),
        "requests_draft": count(RecordRequest, RecordRequest.status == RequestStatus.DRAFT),
        "requests_awaiting_approval": count(RecordRequest, RecordRequest.status == RequestStatus.AWAITING_APPROVAL),
        "requests_submitted": count(RecordRequest, RecordRequest.status == RequestStatus.SUBMITTED),
        "sources_total": count(CollectionSource),
        "collection_runs_failed": count(CollectionRun, CollectionRun.status == "failed"),
    }
