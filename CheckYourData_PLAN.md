# CheckYourData — Project Plan

A data quality & observability tool with an AI agent that analyzes dataset schemas and suggests validation checks. Users can accept AI-suggested checks or pick from manual presets. Results and drift are tracked over time and surfaced on a dashboard.

**Goal:** Working MVP in ~1 week, deployable and demo-able as a portfolio piece.

---

## 1. Tech Stack

| Layer | Choice |
|---|---|
| OS / Dev machine | macOS |
| Backend | Python, FastAPI |
| Frontend | React |
| Database | PostgreSQL (local via Docker, hosted via Railway/Render/Supabase later) |
| AI Agent | Claude API (Anthropic) |
| Containerization | Docker + docker-compose |
| Deployment | Render or Railway (free tier) |
| Version control | GitHub |

---

## 2. Core Design Principle

The AI agent and the manual preset checks both compile down to the **same underlying check-config schema**. The agent is a smart *generator* of check configs — it never runs checks directly and never auto-applies them. All AI-suggested checks go through a **suggest → user approves/edits → save → run** flow. This keeps the core engine deterministic, testable, and demo-safe (no unpredictable agent behavior at runtime).

---

## 3. Build Phases

### Phase 1 — Core Engine (no UI, no agent)
Goal: a working, testable Python package that runs checks against a dataset and stores results.

- [x] Define the check-config schema (JSON), e.g.:
  ```json
  {
    "column": "age",
    "check_type": "not_null",
    "params": {}
  }
  ```
  Table-level checks omit `column`.

  **Check types to support in v1**, organized by category (keep this as a `CheckCategory` enum in code — it's a good design point to bring up in interviews):

  *Column-level*
  - `not_null` / `null_percentage_max`
  - `unique` / `uniqueness_percentage_min`
  - `min_max_range` (numeric bounds)
  - `allowed_values` (categorical whitelist)
  - `regex_match` (emails, phone numbers, custom patterns)
  - `data_type_check` (catches silent type coercion)
  - `string_length_range`
  - `date_range` (e.g. not in the future)
  - `no_duplicates_across_columns` (composite key uniqueness)

  *Distribution / statistical*
  - `mean_within_pct` (vs. historical baseline)
  - `median_within_pct`
  - `std_dev_within_pct`
  - `percentile_range` (e.g. p95 bound)
  - `outlier_rate_max` (% beyond N std devs)
  - `distribution_shift` (KL divergence or PSI vs. baseline — the one "serious" statistical check, worth having even just one)

  *Table-level*
  - `row_count_min` / `row_count_max`
  - `row_count_change_pct` (vs. last run — catches gradual shrink/growth)
  - `column_count_match`
  - `column_order_match` (optional)
  - `freshness_check` (latest timestamp not older than X hours)

  *Cross-column*
  - `referential_check` (values in col A must exist in a reference set)
  - `conditional_check` (if col A = X, col B must satisfy Y)

  Not every check type needs to be built in the first pass through Phase 1 — get the check-runner architecture working with ~5-6 checks across categories first (one from each category), confirm the pattern is easy to extend, then fill in the rest. Trying to build all ~20 before testing the runner is a good way to stall.
- [x] Build the check-runner: takes a dataset (pandas DataFrame) + list of check configs → returns pass/fail + details per check.
- [x] Define the results data model and store results in Postgres (see Section 4).
- [x] Implement baseline/drift comparison: each run compares numeric/categorical stats against the last N runs.
- [x] Test against 2–3 messy datasets, run multiple times (simulate drift by editing a copy of the dataset between runs) to confirm drift detection actually fires. (Used synthetic generated fixtures instead of Kaggle downloads — see `tests/fixtures/generate_messy_data.py`.)
- [x] Write unit tests for each check type.

**Exit criteria:** you can run a Python script that loads a CSV, runs a list of checks, and see correct pass/fail + drift output printed or logged.

---

### Phase 2 — API Layer
Goal: expose the engine as a proper service.

- [x] `POST /datasets/upload` — upload CSV, store metadata + sample rows
- [x] `GET /datasets/{id}/schema` — return inferred schema (column names, types, sample values)
- [x] `POST /datasets/{id}/suggest-checks` — route stubbed (501, "implemented in Phase 3"); actual Claude agent wiring happens in Phase 3
- [x] `POST /datasets/{id}/checks` — save approved/edited check configs for this dataset
- [x] `POST /datasets/{id}/run-checks` — run saved checks against current data, store results
- [x] `GET /datasets/{id}/history` — return past run results for dashboard/trend charts
- [x] `GET /datasets/{id}/checks` — list current active checks for a dataset

**Exit criteria:** all endpoints testable via curl/Postman, backed by Postgres, no frontend needed yet.

---

### Phase 3 — Schema-Analysis Agent
Goal: Claude-powered endpoint that proposes checks.

- [x] Prompt design: input = column names, inferred pandas dtypes, a small sample of rows (~10–20, not the full dataset)
- [x] Ask Claude to infer semantic column types (email, categorical, ID, timestamp, etc.) and propose checks per column
- [x] Force structured JSON output matching the Phase 1 check-config schema exactly (used forced tool-use instead of a JSON-only system prompt — more reliable)
- [x] Validate the agent's output against the schema before showing it to the user (reject/retry malformed output) — also added required-param-key validation to `CheckConfig` itself after a real test run caught the agent using a wrong param key
- [x] Wire this into `POST /datasets/{id}/suggest-checks`

**Exit criteria:** uploading a new, unseen CSV returns a sensible list of suggested checks without manual config.

---

### Phase 4 — Frontend (React)
Goal: usable web UI end-to-end.

- [ ] Upload page — drag/drop CSV
- [ ] Schema + suggested checks view — table of AI suggestions with accept/edit/reject per check, plus a manual "add preset check" option
- [ ] Save & run — trigger a check run, show live pass/fail results
- [ ] History/dashboard page — trend charts per check over multiple runs, drift highlighted visually
- [ ] Basic auth/session isn't needed for a portfolio demo — skip unless time allows

**Exit criteria:** a stranger can go to the site, upload a CSV, see suggested checks, approve them, run them, and see results — with zero explanation needed.

---

### Phase 5 — Docker + Deployment
- [x] Dockerfile for backend, Dockerfile for frontend (or serve frontend build as static files from FastAPI to simplify deployment) — went with single-service: one multi-stage Dockerfile builds the frontend then serves it as static files from FastAPI (verified locally: routing precedence, asset serving, SPA fallback, HEAD requests all confirmed working)
- [x] docker-compose for local dev (backend + frontend + Postgres) — `docker compose up --build` runs Postgres + the single app service
- [x] Deploy Postgres (Railway/Supabase managed free tier) — Supabase, using the session pooler connection string (the direct `db.*.supabase.co` host is IPv6-only and didn't resolve from Docker/most hosts)
- [x] Deploy backend + frontend (Render or Railway) — Render, single web service from the repo-root Dockerfile
- [x] Confirm live link works end-to-end from a fresh browser session — https://checkyourdata.onrender.com verified directly: upload, AI-suggested checks (Claude), save, run-checks (16/18 correctly passed/failed on real messy data), and history all confirmed working against the live service

---

### Phase 6 — Optional / Stretch (only after MVP is live)
- [ ] Scheduled re-runs (cron) so the same dataset is re-checked periodically to show ongoing observability, not just one-off validation
- [ ] Slack/email webhook alert on check failure
- [ ] Support pointing at a live data source URL instead of just file upload

---

## 3a. Key Implementation Decisions (v1)

- **Upload size:** cap it (e.g. 10-20MB) for v1. No chunked/streaming processing now — not worth the effort for a portfolio demo. Note as a known limitation in the README ("v1 caps uploads; production version would stream/chunk").
- **Claude API cost control:** hash the schema + sample rows sent to the agent (`hashlib.sha256`). Before calling the API, check a simple cache (dict or a `schema_cache` table: `hash → suggested_checks_json`) for an existing result on that exact hash. Avoids repeated API calls while testing the same file. No Redis needed for v1 — in-memory or a DB table is fine.
- **Preventing duplicate run submissions:** don't solve this with backend dedup logic — you need multiple runs over time for drift detection to work at all, so don't collapse them. Instead, disable the "Run Checks" button on click, re-enable on response (frontend-only fix).
- **Error handling (v1):** surface actual exception/validation messages in the API response and show them plainly in the UI — no generic "something went wrong" swallowing. This is also more useful for you during development. Retry logic / graceful fallback UX can come later.
- **Demo polish (seed data, screenshots, README depth):** deferred until the core app works end-to-end. Revisit once Phases 1-4 are functional.

---

## 4. Data Model (Postgres, rough draft)

- `datasets` — id, name, uploaded_at, column_schema (JSON), row_count
- `checks` — id, dataset_id, column, check_type, params (JSON), source (`ai_suggested` / `manual`), active (bool)
- `check_runs` — id, dataset_id, run_at
- `check_results` — id, check_run_id, check_id, passed (bool), details (JSON)
- `baseline_stats` — id, dataset_id, column, stat_type, value, computed_at (for drift comparison)

---

## 5. Interview Story (keep this in mind while building)

The pitch: *"I built a data quality/observability tool — similar in spirit to Great Expectations or Monte Carlo — that monitors datasets for schema drift, null spikes, and distribution shift over time, with an AI agent layer that proposes checks automatically from a dataset's schema, which the user reviews and approves before anything runs."*

Be ready to explain:
- Why suggest-and-approve instead of auto-apply (safety, control, realistic production pattern)
- How drift detection works (baseline comparison across runs, not just single-point validation)
- Why the agent output is validated against a strict schema before use
- Trade-offs you made (e.g., check types supported in v1 vs. deferred)

---

## 6. Timeline Target

Realistic 1-week push for Phases 1–4 (MVP), with Phase 5 (deploy) immediately after so there's a live, shareable link. Phase 6 only if time allows — do not let it block shipping the MVP.
