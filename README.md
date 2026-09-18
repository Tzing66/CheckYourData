# CheckYourData

A data quality & observability tool with an AI agent that analyzes dataset schemas and suggests validation checks.

See `CheckYourData_PLAN.md` for the full build plan.

## Phase 1 — Core Engine

```bash
docker compose up -d postgres
cp .env.example .env
uv sync
# or, without uv: pip install -r requirements.txt

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

Endpoints (all under `/datasets`): `POST /upload`, `GET /{id}/schema`, `POST /{id}/suggest-checks`, `POST /{id}/checks`, `GET /{id}/checks`, `POST /{id}/run-checks`, `GET /{id}/history`.

## Phase 3 — Schema-Analysis Agent

`POST /datasets/{id}/suggest-checks` calls Claude (forced tool-use for structured output) with the dataset's column schema + a small sample, and returns a `list[CheckConfig]` your frontend flow would let a user review/edit before submitting to `POST /{id}/checks` — the agent never runs checks or saves anything itself.

```bash
# add your key to .env first:
#   ANTHROPIC_API_KEY=sk-ant-...
#   ANTHROPIC_MODEL=   # optional, defaults to claude-haiku-4-5-20251001
```

- Structured output is forced via a single `propose_checks` tool call (not "please respond in JSON"), with the exact param keys per `check_type` spelled out in the tool description (`agent.PARAM_HINTS`) so Claude doesn't have to guess key names.
- `CheckConfig` now validates required param keys per `check_type` (`schema.REQUIRED_PARAMS`), so a malformed suggestion (wrong/missing param key) is caught and retried automatically (`agent.suggest_checks`, `max_attempts=2`) instead of surfacing at check-run time.
- Results are cached in Postgres (`schema_cache` table, keyed by a sha256 hash of the schema+sample) so re-suggesting on the same data doesn't re-hit the API — verified: a second call for the same dataset returns identically and in ~40ms instead of ~4s.
- The unit test suite (`tests/test_agent.py`) mocks the Claude call entirely — no real API calls or cost in `uv run pytest`.

Known v1 limitations (by design, see `CheckYourData_PLAN.md`):
- No Alembic — tables are created via `Base.metadata.create_all()`.
- Uploads/CSVs are not chunked or streamed; capped at `storage.MAX_UPLOAD_MB` (20MB).
- Uploaded CSVs are stored on local disk (`uploads/`), not in Postgres.
- `params` values themselves aren't type/range-validated (e.g. Claude could still propose a nonsensical `min > max`); only required-key presence is checked.

## Phase 4 — Frontend (React)

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev             # http://localhost:5173
```

Vite + React + TypeScript, Tailwind v4, a few Radix UI primitives (Dialog/Select/Checkbox) for accessible interactive components, `motion` for page transitions and micro-interactions, Recharts for the history trend view, `lucide-react` for icons. One page per route (`/`, `/datasets/:id`, `/datasets/:id/history`) under a persistent header showing the current dataset's name (via the `GET /datasets/{id}` endpoint added alongside this phase). No frontend test framework for v1 — verified by hand against the real API + Postgres.

## Dependency files

- `pyproject.toml` / `uv.lock` — source of truth, used by `uv run`/`uv sync`.
- `requirements.txt` — generated from `uv.lock` (`uv export --format requirements-txt --no-dev --no-hashes -o requirements.txt`) for environments that expect plain pip; regenerate after any dependency change.
- `frontend/package.json` / `package-lock.json` — frontend deps, used by `npm install`.
