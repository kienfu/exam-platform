# Exam Platform (QuizAI)

AI-assisted multiple-choice exam platform: question bank, exam builder, Word/PDF export and
scan-based grading of paper answer sheets. Product behavior is defined in `docs/PRD.md`;
milestones are in `docs/PLAYBOOK.md`.

No Docker and no Redis in this phase. Everything runs directly on Windows.

## Prerequisites

- Python via [uv](https://docs.astral.sh/uv/) (uv installs Python 3.12 on demand)
- Node.js 22+ and pnpm 10 (see below)
- PostgreSQL 16 or newer (see below)

### Install PostgreSQL locally on Windows

1. Download the Windows installer from <https://www.postgresql.org/download/windows/> (EDB) and
   run it. Keep the defaults: port `5432`, install Command Line Tools, and set a password for the
   `postgres` superuser (remember it).
2. The installer registers a Windows service (`postgresql-x64-16` or similar) that starts
   automatically. Check it in `services.msc`, or run `pg_isready` from the PostgreSQL `bin` folder.
3. Create the application role and the two databases (run `psql -U postgres` from the `bin`
   folder, enter the superuser password, then):

   ```sql
   CREATE ROLE quizai WITH LOGIN PASSWORD 'choose-a-password';
   CREATE DATABASE quizai OWNER quizai;
   CREATE DATABASE quizai_test OWNER quizai;
   ```

   `quizai` is for normal runs; `quizai_test` is used by `pytest` (its tables are dropped and
   recreated on every test run, so never point it at real data).

### pnpm

pnpm is provided by Corepack, which ships with Node. If `corepack enable` fails with `EPERM`
(Node installed under `C:\Program Files`), enable it into a folder you own and add that folder to
your PATH:

```powershell
corepack enable --install-directory $HOME\corepack-bin
corepack prepare pnpm@10.15.0 --activate
```

## Setup

```powershell
copy .env.example .env      # then put the quizai password into both database URLs
cd backend
uv sync
uv run alembic upgrade head
cd ..\frontend
pnpm install
```

`.env` is git-ignored. Never commit it.

## Run (three terminals)

```powershell
cd backend;  uv run uvicorn app.main:app --reload     # API on http://localhost:8000 (/health, /docs)
cd backend;  uv run python -m app.worker              # background worker
cd frontend; pnpm dev                                 # web on http://localhost:5173
```

Try the sample job: with the worker running, enqueue one from a Python shell
(`cd backend; uv run python`):

```python
from app.db.session import get_session_factory
from app.jobs.pg_queue import PgJobQueue
PgJobQueue(get_session_factory()).enqueue("sample.echo", {"hello": "world"})
```

The worker logs `sample.echo payload={'hello': 'world'}`.

## Test and lint

```powershell
cd backend;  uv run pytest; uv run ruff check .; uv run mypy
cd frontend; pnpm test; pnpm lint; pnpm build
```

## API client

The frontend client is generated from the backend OpenAPI schema. After changing any endpoint:

```powershell
cd frontend; pnpm gen:api
```

This rewrites `frontend/openapi.json` and `frontend/src/api/schema.d.ts`. Commit both. CI fails if
they are stale.

## Layout

- `backend/app/jobs`: `JobQueue` interface, PostgreSQL implementation (`FOR UPDATE SKIP LOCKED`),
  handler registry
- `backend/app/worker.py`: worker entry point
- `docs/decisions`: architecture decision records
