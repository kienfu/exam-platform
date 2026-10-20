"""Enqueue one sample.echo job. Usage: python scripts/enqueue_sample.py [--fail] [message]."""

import sys

from app.db.session import get_session_factory
from app.jobs.pg_queue import PgJobQueue

args = [a for a in sys.argv[1:] if a != "--fail"]
payload = {"message": args[0] if args else "hello", "fail": "--fail" in sys.argv[1:]}
job_id = PgJobQueue(get_session_factory()).enqueue("sample.echo", payload)
print(f"enqueued job {job_id}: {payload}")
