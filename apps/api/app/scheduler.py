import logging
import time

from app.worker import enqueue_due_collections

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Single scheduler process; workers remain stateless and horizontally scalable."""
    while True:
        try:
            queued = enqueue_due_collections()
            if queued:
                logger.info("Queued %s due collection(s)", queued)
        except Exception:
            logger.exception("Unable to schedule due source collections")
        time.sleep(60)


if __name__ == "__main__":
    main()
