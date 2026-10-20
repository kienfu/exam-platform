"""Start the real API and worker entry points as separate processes (PRD 8.5).

`uv run uvicorn ...` and `uv run python -m app.worker` run these same modules in the
project virtualenv, so sys.executable stands in for `uv run`. Both talk to the test database.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.jobs.pg_queue import PgJobQueue
from app.models.job import Job

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    return {
        **os.environ,
        "DATABASE_URL": get_settings().test_database_url,
        "WORKER_POLL_INTERVAL_SECONDS": "0.2",
    }


@contextmanager
def _process(args: list[str], log: Path) -> Iterator[subprocess.Popen[bytes]]:
    with log.open("wb") as out:
        proc = subprocess.Popen(
            [sys.executable, *args], cwd=BACKEND_DIR, env=_env(), stdout=out, stderr=out
        )
        try:
            yield proc
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def test_uvicorn_entry_point_serves_health(engine: object, tmp_path: Path) -> None:
    port = _free_port()
    args = ["-m", "uvicorn", "app.main:app", "--port", str(port)]
    with _process(args, tmp_path / "api.log") as proc:
        body = None
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and body is None:
            assert proc.poll() is None, (tmp_path / "api.log").read_text(errors="replace")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                    assert r.status == 200
                    body = r.read().decode()
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.3)
    assert body is not None, "API did not answer /health in time"
    assert '"status":"ok"' in body.replace(" ", "")


def test_worker_entry_point_runs_the_sample_job(
    session_factory: sessionmaker[Session], tmp_path: Path
) -> None:
    log = tmp_path / "worker.log"
    with _process(["-m", "app.worker"], log):
        job_id = PgJobQueue(session_factory).enqueue("sample.echo", {"message": "from smoke test"})
        status = "queued"
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and status != "succeeded":
            time.sleep(0.3)
            with session_factory() as s:
                job = s.get(Job, job_id)
                assert job is not None
                status = job.status
    assert status == "succeeded"
    output = log.read_text(errors="replace")
    assert "worker" in output and "started" in output
    assert "sample.echo payload=" in output and "from smoke test" in output
