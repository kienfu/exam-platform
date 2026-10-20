import logging
import os
import signal
import socket
import threading
from types import FrameType

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.jobs.pg_queue import PgJobQueue
from app.jobs.queue import JobQueue
from app.jobs.registry import Handler, default_handlers

logger = logging.getLogger("app.worker")


def process_one(queue: JobQueue, handlers: dict[str, Handler], worker_id: str) -> bool:
    """Claim and run a single job. Returns False when nothing was due."""
    job = queue.claim(worker_id)
    if job is None:
        return False
    handler = handlers.get(job.type)
    try:
        if handler is None:
            raise LookupError(f"no handler registered for job type {job.type!r}")
        handler(job.payload)
    except Exception as exc:
        logger.exception("job %s (%s) failed on attempt %s", job.id, job.type, job.attempts)
        queue.fail(job.id, f"{type(exc).__name__}: {exc}")
    else:
        queue.complete(job.id)
    return True


def run(queue: JobQueue, handlers: dict[str, Handler], stop: threading.Event) -> None:
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    poll = get_settings().worker_poll_interval_seconds
    logger.info("worker %s started", worker_id)
    while not stop.is_set():
        if not process_one(queue, handlers, worker_id):
            stop.wait(poll)
    logger.info("worker %s stopped", worker_id)


def main() -> None:
    logging.basicConfig(
        level=get_settings().log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    stop = threading.Event()

    def _stop(signum: int, frame: FrameType | None) -> None:
        stop.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    run(PgJobQueue(get_session_factory()), default_handlers(), stop)


if __name__ == "__main__":
    main()
