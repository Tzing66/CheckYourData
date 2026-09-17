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

Known v1 limitations (by design, see `CheckYourData_PLAN.md`):
- No Alembic — tables are created via `Base.metadata.create_all()`.
- Uploads/CSVs are not chunked or streamed.
