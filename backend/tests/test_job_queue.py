import threading
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.jobs.pg_queue import PgJobQueue
from app.jobs.registry import default_handlers
from app.models.job import Job
from app.worker import process_one


def _job(factory: sessionmaker[Session], job_id: int) -> Job:
    with factory() as s:
        job = s.get(Job, job_id)
        assert job is not None
        return job


def test_claim_returns_none_when_empty(session_factory: sessionmaker[Session]) -> None:
    assert PgJobQueue(session_factory).claim("w1") is None


def test_enqueue_claim_complete(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory)
    job_id = queue.enqueue("sample.echo", {"n": 1})
    claimed = queue.claim("w1")
    assert claimed is not None
    assert (claimed.id, claimed.type, claimed.payload, claimed.attempts) == (
        job_id,
        "sample.echo",
        {"n": 1},
        1,
    )
    assert _job(session_factory, job_id).status == "running"
    assert queue.claim("w2") is None
    queue.complete(job_id)
    assert _job(session_factory, job_id).status == "succeeded"


def test_future_job_is_not_claimed(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory)
    queue.enqueue("sample.echo", run_at=datetime.now(UTC) + timedelta(hours=1))
    assert queue.claim("w1") is None


def test_concurrent_claims_never_share_a_job(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory)
    ids = {queue.enqueue("sample.echo", {"i": i}) for i in range(20)}
    claimed: list[int] = []
    lock = threading.Lock()

    def drain(worker: str) -> None:
        while (job := queue.claim(worker)) is not None:
            with lock:
                claimed.append(job.id)

    threads = [threading.Thread(target=drain, args=(f"w{i}",)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(claimed) == sorted(ids)


def test_fail_requeues_with_backoff_then_dies(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory)
    job_id = queue.enqueue("sample.echo", max_attempts=2)

    assert queue.claim("w1") is not None
    queue.fail(job_id, "boom")
    job = _job(session_factory, job_id)
    assert job.status == "queued"
    assert job.last_error == "boom"
    assert queue.claim("w1") is None  # backing off

    with session_factory() as s:
        s.get(Job, job_id).run_at = datetime.now(UTC) - timedelta(seconds=1)  # type: ignore[union-attr]
        s.commit()
    assert queue.claim("w1") is not None
    queue.fail(job_id, "boom again")
    assert _job(session_factory, job_id).status == "dead"


def test_stale_running_job_is_reclaimed(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory, visibility_timeout_seconds=60)
    job_id = queue.enqueue("sample.echo")
    assert queue.claim("crashed") is not None
    with session_factory() as s:
        s.get(Job, job_id).locked_at = datetime.now(UTC) - timedelta(minutes=5)  # type: ignore[union-attr]
        s.commit()
    reclaimed = queue.claim("w2")
    assert reclaimed is not None
    assert reclaimed.attempts == 2


def test_worker_runs_sample_job(session_factory: sessionmaker[Session]) -> None:
    queue = PgJobQueue(session_factory)
    job_id = queue.enqueue("sample.echo", {"hello": "world"})
    assert process_one(queue, default_handlers(), "w1") is True
    assert _job(session_factory, job_id).status == "succeeded"
    assert process_one(queue, default_handlers(), "w1") is False


def test_worker_fails_job_on_handler_error_and_unknown_type(
    session_factory: sessionmaker[Session],
) -> None:
    queue = PgJobQueue(session_factory)
    failing = queue.enqueue("sample.echo", {"fail": True})
    unknown = queue.enqueue("nope")
    assert process_one(queue, default_handlers(), "w1") is True
    assert process_one(queue, default_handlers(), "w1") is True
    for job_id, text in ((failing, "asked to fail"), (unknown, "no handler")):
        job = _job(session_factory, job_id)
        assert job.status == "queued"
        assert job.last_error is not None and text in job.last_error
