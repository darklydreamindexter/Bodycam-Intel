from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Case, Scorecard
from app.schemas import CaseCreate, CaseRead, ScorecardCreate, ScorecardRead
from app.services import create_case, create_scorecard

router = APIRouter()


@router.get("", response_model=list[CaseRead])
def list_cases(db: Session = Depends(get_db)) -> list[Case]:
    return list(db.scalars(select(Case).order_by(Case.created_at.desc())))


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case_endpoint(payload: CaseCreate, db: Session = Depends(get_db)) -> Case:
    return create_case(db, payload)


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: UUID, db: Session = Depends(get_db)) -> Case:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return case


@router.get("/{case_id}/scorecards", response_model=list[ScorecardRead])
def list_scorecards(case_id: UUID, db: Session = Depends(get_db)) -> list[Scorecard]:
    return list(db.scalars(select(Scorecard).where(Scorecard.case_id == case_id).order_by(Scorecard.created_at.desc())))


@router.post("/{case_id}/scorecards", response_model=ScorecardRead, status_code=status.HTTP_201_CREATED)
def score_case(case_id: UUID, payload: ScorecardCreate, db: Session = Depends(get_db)) -> Scorecard:
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return create_scorecard(db, case, payload)
