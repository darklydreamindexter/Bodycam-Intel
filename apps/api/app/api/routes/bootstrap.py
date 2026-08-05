from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import Agency, Case, RecordRequest, RequestStatus
from app.services import _record_event

router = APIRouter()


@router.post("/demo", status_code=status.HTTP_201_CREATED)
def create_demo_data(db: Session = Depends(get_db)) -> dict[str, str]:
    """Populate explicit demo records for local dashboard exploration only."""
    if get_settings().environment != "local":
        raise HTTPException(status_code=403, detail="Demo data is only available in the local environment.")
    existing = db.scalar(select(Agency).where(Agency.name == "Demo City Police Department"))
    if existing:
        return {"message": "Demo data already exists."}

    agency = Agency(
        name="Demo City Police Department",
        agency_type="police_department",
        city="Demo City",
        county="Example County",
        state="TX",
        records_email="records@example.invalid",
        retention_notes="Demonstration data only — not a real agency or contact.",
    )
    db.add(agency)
    db.flush()
    case = Case(
        title="DEMO — Traffic pursuit and arrest",
        summary="Registro fictício criado apenas para explorar o fluxo local da plataforma.",
        occurred_at=datetime.now(timezone.utc),
        city="Demo City",
        county="Example County",
        state="TX",
        confidence=75,
        primary_agency_id=agency.id,
        source_urls=["https://example.invalid/demo"],
    )
    db.add(case)
    db.flush()
    request = RecordRequest(
        case_id=case.id,
        agency_id=agency.id,
        status=RequestStatus.DRAFT,
        subject="DEMO — Public records request draft",
        body="This fictional draft is for local interface testing only.",
        requested_items=["Body-Worn Camera Footage", "CAD Logs"],
    )
    db.add(request)
    _record_event(db, "bootstrap.demo_created", "case", case.id, "bootstrap.demo_created", {"demo": True})
    db.commit()
    return {"message": "Local demo data created."}
