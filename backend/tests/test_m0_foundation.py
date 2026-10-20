"""M0 definition-of-done checks that are not covered by the feature tests."""

import json
import subprocess
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import Engine

import app.models  # noqa: F401  (register tables on Base.metadata)
from app.db.base import Base
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git_ignored(path: str) -> bool:
    result = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO_ROOT, check=False)
    return result.returncode == 0


def test_gitignore_blocks_secrets_and_uploaded_data() -> None:
    for path in (".env", ".env.local", "backend/.env", "data/uploads/scan.jpg", "uploads/a.jpg"):
        assert _git_ignored(path), f"{path} must be git-ignored"
    assert not _git_ignored(".env.example"), ".env.example must be committed"


def test_env_file_is_not_tracked() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env", "frontend/.env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert tracked.strip() == ""


def test_committed_openapi_schema_is_current() -> None:
    committed = json.loads((REPO_ROOT / "frontend" / "openapi.json").read_text(encoding="utf-8"))
    assert committed == app.openapi(), "run `pnpm gen:api` in frontend/ and commit the result"


def test_migrations_match_models(engine: Engine) -> None:
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == [], f"models and Alembic migrations differ: {diff}"


def test_cors_allows_the_web_origin_only() -> None:
    client = TestClient(app)
    preflight = {"Access-Control-Request-Method": "GET"}
    allowed = client.options("/health", headers={"Origin": "http://localhost:5173", **preflight})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    blocked = client.options("/health", headers={"Origin": "http://evil.example", **preflight})
    assert "access-control-allow-origin" not in blocked.headers


def test_route_inventory_is_explicit() -> None:
    """CLAUDE.md rule 7: every endpoint needs an authz test.

    M0 has no business endpoints; /health is public on purpose. Adding a route must
    update this set, which is the prompt to write its authz test.
    """
    # app.routes does not flatten included routers in current FastAPI, so list the
    # documented API surface from the schema and the directly mounted routes separately.
    documented = set(app.openapi()["paths"])
    mounted = {r.path for r in app.routes if hasattr(r, "path")}
    framework = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
    assert documented == {"/health"}
    assert mounted <= framework, f"undocumented routes need an authz test: {mounted - framework}"
