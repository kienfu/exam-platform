# 001. Stack and local-first environment

Status: accepted (M0)

## Context

PRD sections 2 (D12, D13) and 8 define the stack. The first phase runs on a Windows machine with
no Docker and no Redis. Background work (AI generation, grading, exports) must still run in a
separate process, and must be replaceable by Redis + RQ at deploy time without touching business
code.

## Decision

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, managed with uv.
  Driver: psycopg 3 (`postgresql+psycopg://`), which SQLAlchemy 2.0 supports natively and which
  ships binary wheels for Windows.
- **Database:** PostgreSQL installed as a Windows service. Separate `quizai` and `quizai_test`
  databases. Schema changes only through Alembic.
- **Job queue:** business code and the worker depend on the `JobQueue` protocol
  (`app/jobs/queue.py`). `PgJobQueue` stores jobs in a `jobs` table. A worker claims the next
  due job with `SELECT ... FOR UPDATE SKIP LOCKED` and marks it `running` in the same
  transaction, so concurrent workers never take the same job.
  - Failure: requeued with exponential backoff (5s, 10s, ...) until `max_attempts`, then `dead`.
  - A `running` job whose lock is older than the visibility timeout (default 300s) is handed out
    again, so a crashed worker does not lose work. Handlers must therefore be idempotent (PRD 8.4).
  - The worker is a single polling process (`uv run python -m app.worker`). The configurable
    worker count from PRD 8.4 is deferred to the grading milestone; until then, run more
    processes to scale out.
- **Frontend:** React, Vite, TypeScript, TanStack Query, React Router, Tailwind v4, pnpm.
  The API client is generated from the backend OpenAPI schema with `openapi-typescript`, used
  through `openapi-fetch`. The schema is exported by `backend/scripts/export_openapi.py` and both
  generated files are committed, so CI can detect drift.
- **TypeScript:** pinned to 5.9. `openapi-typescript` needs the TypeScript compiler API, which
  TypeScript 7 (the native port) does not provide.
- **Lint and tests:** ruff, mypy (strict for `app/omr` and `app/services`), pytest; oxlint,
  Prettier, Vitest. Playwright e2e is added in a later milestone.
- **CI:** GitHub Actions, one job per side; the backend job uses a PostgreSQL 16 service.

## Consequences

- No Docker or Redis to install; developer setup is PostgreSQL plus three terminals.
- Polling adds up to one poll interval (default 1s) of latency to job pickup. Acceptable for
  the workloads in the PRD.
- Moving to Redis + RQ later means writing one new `JobQueue` implementation. Job state in
  PostgreSQL can be dropped at that point.
- `/health` is deliberately unauthenticated. It exposes only liveness and database reachability.
