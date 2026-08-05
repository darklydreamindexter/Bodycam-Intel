import dramatiq
from dramatiq.brokers.redis import RedisBroker
from uuid import UUID

from app.config import get_settings
from app.db import SessionLocal
from app.services import collect_rss_source, schedule_due_sources

broker = RedisBroker(url=get_settings().redis_url)
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=3)
def process_outbox_event(event_id: str) -> None:
    """Reserved consumer boundary for future notifications, enrichments and collectors."""
    print(f"Received outbox event {event_id}")


@dramatiq.actor(max_retries=2, min_backoff=30_000)
def collect_source(source_id: str, trigger: str = "scheduled") -> None:
    db = SessionLocal()
    try:
        collect_rss_source(db, UUID(source_id), trigger)
    finally:
        db.close()


def enqueue_due_collections() -> int:
    db = SessionLocal()
    try:
        source_ids = schedule_due_sources(db)
    finally:
        db.close()
    for source_id in source_ids:
        collect_source.send(source_id, "scheduled")
    return len(source_ids)
