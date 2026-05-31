# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

LLM-based movie review opinion structuring system. Pipeline: reviews → LLM phrase + sentiment extraction → embedding + HDBSCAN clustering → final summary (top opinions + sentiment ratio) consumed by a Next.js frontend. Designed as a daily batch job system, not real-time analysis.

The backend (`app/`) is the orchestrator (role "B" in the design doc): it owns job state, calls the LLM module ("C"), calls the clustering module ("D"), and exposes the final read API to the frontend ("A"). README.md (Korean) is the authoritative design doc — read it before non-trivial schema or pipeline work.

## Commands

Backend uses `uv` as the package manager (Python 3.12+).

```powershell
# Install / sync dependencies
uv sync

# Run API (FastAPI on :8000, CORS allows http://localhost:3000)
uv run uvicorn app.main:app --reload

# DB migrations (Alembic, target = app.db.base.Base.metadata)
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"

# Seed PostgreSQL from data/movies.json + data/reviews_dataset.json
uv run python scripts/seed_data.py
```

Frontend (Next.js 16, in `frontend/`):

```powershell
npm install
npm run dev      # dev server on :3000
npm run build
npm run lint
```

`.env` at repo root must define `database_url` (consumed via `app/core/config.py` → `pydantic-settings`). `OPENAI_API_KEY` is optional — only needed for `llm_mode=openai`; otherwise the LLM module silently falls back to rule-based extraction.

## Non-negotiable rules

- Do NOT change API schemas without approval.
- Preserve orchestrator / module separation.
- Prefer incremental edits over large refactors.

## Responsibilities

job_service.py
- orchestration only

llm_service.py
- extraction only

cluster_service.py
- clustering only

result_service.py
- persistence only

## Architecture

### Storage architecture

PostgreSQL (SQLAlchemy 2.0 ORM, `app/db/`) is the single source of truth for all pipeline state. Tables: `movies`, `reviews`, `batch_jobs`, `llm_phrases`, `opinion_groups`, `review_cluster_map`, `movie_summary`. All read and write paths in `app/services/result_service.py` and `app/services/job_service.py` use the DB directly.

JSON files in `data/` (`jobs.json`, `llm_results.json`, `cluster_results.json`, `final_results.json`) are migration-era frozen archives — gitignored, not updated, kept only as historical record/recovery snapshot. `scripts/backfill_*.py` can rebuild DB tables from these archives if ever needed (idempotent, no-op on missing files).

Verification gates in `scripts/`:
- `verify_routes.py` — HTTP contract for read endpoints + POST validation
- `verify_pipeline_e2e.py` — full create→run-llm→run-cluster→build-final flow with cleanup

### Pipeline flow

`POST /batch/jobs` → `run-llm` → `run-cluster` → `build-final`, all keyed by `job_id`. The frontend calls these in sequence (`frontend/lib/api.ts::runBatchPipeline`).

`app/services/job_service.py` is the orchestrator. Each step:
1. **run-llm**: `fetch_reviews` (Postgres) → `LLMRequestSchema` → `extract_phrases_with_sentiment(mode=...)` → save to `llm_phrases` table. Validates `len(input.reviews) == len(output.results)` and raises if not.
2. **run-cluster**: reads `llm_phrases` (via `build_cluster_request_for_job`) → builds `ClusterRequestSchema` → `run_cluster_module(mode=...)` → save to `opinion_groups` table.
3. **build-final**: reads prior DB state → `final_service.build_final_result` → save `review_cluster_map` rows and upsert `movie_summary`.

### Pluggable modes

- **LLM** (`app/services/llm_service.py`, `extract_phrases_with_sentiment`): `dummy` | `rule_based` | `openai`. The OpenAI path falls back to rule-based on missing API key, parse failure, or API error — failures are logged, never raised. `infer_sentiment` is a keyword heuristic applied to every phrase regardless of source mode.
- **Clustering** (`app/services/cluster_service.py`, `run_cluster_module`): `hdbscan` (default, uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) | `kmeans`. Same topic can split into separate clusters by sentiment.

### Schema rules (from README §5 + §9)

- snake_case fields, ISO 8601 datetimes, `is_` prefix for booleans, IDs are strings.
- Module boundaries B↔C and B↔D have fixed JSON shapes — see `app/schemas.py`. `key_phrases` should be short (2–5 per review); long full-sentence phrases break clustering quality.
- Job status is a fixed enum: `queued` → `collecting_reviews` → `llm_processing` → `clustering` → `saving_results` → `completed`, plus `failed`.

### Frontend

Next.js 16.2.4 + React 19 + Tailwind 4. **`frontend/AGENTS.md` warns this version has breaking changes vs. older Next.js** — consult `frontend/node_modules/next/dist/docs/` before writing Next-specific code. The frontend talks to the backend via `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`); types in `frontend/lib/types.ts` mirror the Pydantic schemas.

### Other directories

- `alembic/versions/` — migrations; `alembic/env.py` imports `app.db.models` so autogenerate sees all tables.
