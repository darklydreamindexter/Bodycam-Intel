from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Agency
from app.schemas import AgencyCreate, AgencyRead

router = APIRouter()


@router.get("", response_model=list[AgencyRead])
def list_agencies(db: Session = Depends(get_db)) -> list[Agency]:
    return list(db.scalars(select(Agency).order_by(Agency.name)))


@router.post("", response_model=AgencyRead, status_code=status.HTTP_201_CREATED)
def create_agency(payload: AgencyCreate, db: Session = Depends(get_db)) -> Agency:
    if db.scalar(select(Agency).where(Agency.name == payload.name)):
        raise HTTPException(status_code=409, detail="An agency with this name already exists.")
    agency = Agency(**payload.model_dump(), state=payload.state.upper())
    db.add(agency)
    db.commit()
    db.refresh(agency)
    return agency


@router.get("/{agency_id}", response_model=AgencyRead)
def get_agency(agency_id: UUID, db: Session = Depends(get_db)) -> Agency:
    agency = db.get(Agency, agency_id)
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found.")
    return agency
