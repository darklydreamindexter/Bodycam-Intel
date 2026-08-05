from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CollectionRun, CollectionSource
from app.schemas import CollectionRunRead, CollectionSourceCreate, CollectionSourceRead
from app.services import create_collection_source, reserve_manual_collection
from app.worker import collect_source

router = APIRouter()


@router.get("", response_model=list[CollectionSourceRead])
def list_sources(db: Session = Depends(get_db)) -> list[CollectionSource]:
    return list(db.scalars(select(CollectionSource).order_by(CollectionSource.name)))


@router.post("", response_model=CollectionSourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: CollectionSourceCreate, db: Session = Depends(get_db)) -> CollectionSource:
    if db.scalar(select(CollectionSource).where(CollectionSource.name == payload.name)):
        raise HTTPException(status_code=409, detail="A source with this name already exists.")
    if db.scalar(select(CollectionSource).where(CollectionSource.url == payload.url)):
        raise HTTPException(status_code=409, detail="This source URL is already registered.")
    return create_collection_source(db, payload)


@router.post("/{source_id}/collect", status_code=status.HTTP_202_ACCEPTED)
def enqueue_collection(source_id: UUID, db: Session = Depends(get_db)) -> dict[str, str]:
    source = db.get(CollectionSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Collection source not found.")
    if not source.active:
        raise HTTPException(status_code=409, detail="Collection source is disabled.")
    if not reserve_manual_collection(db, source):
        raise HTTPException(status_code=409, detail="This source is already being collected. Try again shortly.")
    collect_source.send(str(source.id), "manual")
    return {"message": "Collection queued. Refresh this page shortly to see its result."}


@router.get("/runs/recent", response_model=list[CollectionRunRead])
def list_recent_runs(limit: int = 20, db: Session = Depends(get_db)) -> list[CollectionRun]:
    safe_limit = min(max(limit, 1), 100)
    return list(db.scalars(select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(safe_limit)))
