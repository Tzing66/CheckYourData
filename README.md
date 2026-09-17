# CheckYourData

A data quality & observability tool with an AI agent that analyzes dataset schemas and suggests validation checks.

See `CheckYourData_PLAN.md` for the full build plan.

## Phase 1 — Core Engine

```bash
docker compose up -d postgres
cp .env.example .env
uv sync
uv run pytest
```
