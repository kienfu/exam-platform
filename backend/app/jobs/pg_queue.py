from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.jobs.queue import ClaimedJob
from app.models.job import Job

BACKOFF_BASE_SECONDS = 5


class PgJobQueue:
    def __init__(
        self,
        session_factory: Callable[[], Session],
        *,
        visibility_timeout_seconds: int | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._visibility_timeout = timedelta(
            seconds=visibility_timeout_seconds
            if visibility_timeout_seconds is not None
            else get_settings().job_visibility_timeout_seconds
        )

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any] | None = None,
        *,
        run_at: datetime | None = None,
        max_attempts: int | None = None,
    ) -> int:
        job = Job(
            type=job_type,
            payload=payload or {},
            max_attempts=max_attempts or get_settings().job_max_attempts,
        )
        if run_at is not None:
            job.run_at = run_at
        with self._session_factory() as session:
            session.add(job)
            session.commit()
            return job.id

    def claim(self, worker_id: str) -> ClaimedJob | None:
        due = or_(
            (Job.status == "queued") & (Job.run_at <= func.now()),
            # A worker that died mid-job leaves it running; hand it out again.
            (Job.status == "running") & (Job.locked_at < func.now() - self._visibility_timeout),
        )
        stmt = (
            select(Job)
            .where(due)
            .order_by(Job.run_at, Job.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        with self._session_factory() as session:
            job = session.execute(stmt).scalar_one_or_none()
            if job is None:
                return None
            if job.attempts >= job.max_attempts:
                job.status = "dead"
                job.last_error = job.last_error or "abandoned after worker timeout"
                session.commit()
                return None
            job.status = "running"
            job.attempts += 1
            job.locked_at = func.now()
            job.locked_by = worker_id
            session.commit()
            return ClaimedJob(job.id, job.type, job.payload, job.attempts, job.max_attempts)

    def complete(self, job_id: int) -> None:
        with self._session_factory() as session:
            job = session.get(Job, job_id, with_for_update=True)
            if job is None:
                return
            job.status = "succeeded"
            job.locked_at = None
            job.locked_by = None
            session.commit()

    def fail(self, job_id: int, error: str) -> None:
        with self._session_factory() as session:
            job = session.get(Job, job_id, with_for_update=True)
            if job is None:
                return
            job.last_error = error
            job.locked_at = None
            job.locked_by = None
            if job.attempts >= job.max_attempts:
                job.status = "dead"
            else:
                job.status = "queued"
                delay = timedelta(seconds=BACKOFF_BASE_SECONDS * 2 ** (job.attempts - 1))
                job.run_at = func.now() + delay
            session.commit()
