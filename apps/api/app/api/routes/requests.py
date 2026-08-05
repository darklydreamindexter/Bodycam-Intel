from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RecordRequest
from app.schemas import RecordRequestCreate, RecordRequestRead
from app.services import approve_request, create_request_draft, request_approval

router = APIRouter()


@router.get("", response_model=list[RecordRequestRead])
def list_requests(db: Session = Depends(get_db)) -> list[RecordRequest]:
    return list(db.scalars(select(RecordRequest).order_by(RecordRequest.created_at.desc())))


@router.post("", response_model=RecordRequestRead, status_code=status.HTTP_201_CREATED)
def create_draft(payload: RecordRequestCreate, db: Session = Depends(get_db)) -> RecordRequest:
    return create_request_draft(db, payload)


@router.post("/{request_id}/request-approval", response_model=RecordRequestRead)
def send_for_approval(request_id: UUID, db: Session = Depends(get_db)) -> RecordRequest:
    record_request = db.get(RecordRequest, request_id)
    if not record_request:
        raise HTTPException(status_code=404, detail="Request not found.")
    try:
        return request_approval(db, record_request)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/{request_id}/approve", response_model=RecordRequestRead)
def approve_draft(request_id: UUID, db: Session = Depends(get_db)) -> RecordRequest:
    record_request = db.get(RecordRequest, request_id)
    if not record_request:
        raise HTTPException(status_code=404, detail="Request not found.")
    try:
        return approve_request(db, record_request)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
