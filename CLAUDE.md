# Exam Platform

AI-assisted multiple-choice exam platform: question bank, exam builder,
Word/PDF export, and scan-based grading of paper answer sheets.

Read docs/PRD.md before starting any task. It is the source of truth for product behavior.
Milestones, prompts and definitions of done are in docs/PLAYBOOK.md.
If a task conflicts with the PRD, stop and ask before changing anything.

## Stack and commands
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis + RQ, OpenCV.
- Frontend: React, Vite, TypeScript, TanStack Query, Tailwind.
- Start services: `docker compose up -d db redis`
- Backend: `cd backend && uv run pytest`, `uv run ruff check .`, `uv run mypy app`, `uv run alembic upgrade head`
- Frontend: `cd frontend && pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm e2e`

## Non-negotiable rules
1. Locked exams, question revisions, exam version items and the sheet layout JSON are immutable.
2. A submission score is always recomputable from stored answers, version option order and corrections.
3. Student answers are stored by option_id, never by letter.
4. OMR never guesses silently. Any ambiguity sets the submission to needs_review.
5. The layout engine in app/omr is the single source of truth for both the answer sheet PDF and the reader.
6. All LLM calls go through LLMProvider. No provider SDK imports outside app/ai/providers.
7. Authorization and department scoping are enforced in backend dependencies. Every endpoint has an authz test.
8. State-changing actions listed in PRD section 3 write an AuditLog row.
9. UI strings and question content are in English.

## Conventions
- Type hints everywhere; mypy strict for app/omr and app/services.
- Routers stay thin; business logic lives in services/.
- Database changes only through Alembic migrations.
- Tests never use the network. AI is tested with the fake provider.
- Do not add a dependency without saying why.
- Small commits with clear messages. Run lint and tests before saying a task is done.

## Workflow
- Work on one milestone at a time (see docs/PLAYBOOK.md). Start with a plan listing the files you will touch.
- Definition of done: tests pass, lint is clean, the milestone definition of done and the related PRD acceptance criteria are verified, docs updated.
- Record notable decisions in docs/decisions/NNN-title.md.
