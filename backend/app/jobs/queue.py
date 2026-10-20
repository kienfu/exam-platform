from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class ClaimedJob:
    id: int
    type: str
    payload: dict[str, Any]
    attempts: int
    max_attempts: int


class JobQueue(Protocol):
    """Business code and the worker only talk to this interface, so the backing
    store (PostgreSQL today, Redis + RQ later) can be swapped."""

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any] | None = None,
        *,
        run_at: datetime | None = None,
        max_attempts: int | None = None,
    ) -> int: ...

    def claim(self, worker_id: str) -> ClaimedJob | None:
        """Atomically take the next due job, or return None.

        Two workers never receive the same job.
        """
        ...

    def complete(self, job_id: int) -> None: ...

    def fail(self, job_id: int, error: str) -> None:
        """Requeue with backoff, or mark dead once max_attempts is reached."""
        ...
