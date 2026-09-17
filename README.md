# CheckYourData

A data quality & observability tool with an AI agent that analyzes dataset schemas and suggests validation checks.

See `CheckYourData_PLAN.md` for the full build plan.

## Phase 1 — Core Engine

```bash
docker compose up -d postgres
cp .env.example .env
uv sync

# tests (don't need Postgres running, use in-memory SQLite for DB-touching tests)
uv run pytest

# exit-criteria demo: load messy CSVs, run checks, print pass/fail + drift (needs Postgres running)
PYTHONPATH=backend uv run python tests/fixtures/generate_messy_data.py
PYTHONPATH=backend uv run python scripts/demo_run.py
```

## Phase 2 — API Layer

```bash
# serve the API (creates tables on startup)
PYTHONPATH=backend uv run fastapi dev backend/checkyourdata/api/main.py

# interactive docs
open http://127.0.0.1:8000/docs
```

Endpoints (all under `/datasets`): `POST /upload`, `GET /{id}/schema`, `POST /{id}/suggest-checks` (stub — 501 until Phase 3), `POST /{id}/checks`, `GET /{id}/checks`, `POST /{id}/run-checks`, `GET /{id}/history`.

Known v1 limitations (by design, see `CheckYourData_PLAN.md`):
- No Alembic — tables are created via `Base.metadata.create_all()`.
- Uploads/CSVs are not chunked or streamed; capped at `storage.MAX_UPLOAD_MB` (20MB).
- Uploaded CSVs are stored on local disk (`uploads/`), not in Postgres.
