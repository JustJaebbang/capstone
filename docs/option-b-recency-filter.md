# Option B — Scheduled Batch Recency Filter

## What this is

A small, future code change for the nightly collection batch (`app/services/collection_service.py::refresh_all_subscribed_movies`). Adds a filter so the batch only refreshes movies that were requested within the last N days, instead of every movie that's ever been collected.

## Why this isn't applied now

Capstone scope (≤50 movies, ~30-day demo window) makes both DB growth (~12MB max) and batch time (~8 min/night max) negligible. Adding the filter prematurely:

- Hides any subtle batch bugs by reducing the dataset
- Could mask data we want to see in the demo
- Adds a maintenance knob nobody is asking for yet

The current "refresh everything ever requested" design also helps with [[supabase-keepalive-non-negotiable]] — the daily cron acts as a natural keepalive ping. A recency filter that drops to zero subscribed movies would silently disable that benefit. Reapply this filter only after Step 7+8 are stable.

## When to apply this

Apply when **any** of:

1. The subscribed-movie count crosses ~50 (batch time > ~8 min/night)
2. The nightly batch starts running into morning hours / blocking demos
3. `collection_jobs` row growth becomes visible on Supabase dashboard
4. Post-demo, transitioning into long-term maintenance mode

Don't apply during active capstone development just to "clean things up."

## Implementation

### 1. Code change — single filter line

File: `app/services/collection_service.py`

Find this block in `refresh_all_subscribed_movies()`:

```python
rows = (
    db.query(
        CollectionJob.target_movie_id,
        CollectionJob.source,
        CollectionJob.source_external_id,
    )
    .filter(CollectionJob.source_external_id.isnot(None))
    .distinct()
    .all()
)
```

Add the recency filter:

```python
from datetime import datetime, timedelta

RECENCY_WINDOW_DAYS = 14  # tunable

rows = (
    db.query(
        CollectionJob.target_movie_id,
        CollectionJob.source,
        CollectionJob.source_external_id,
    )
    .filter(CollectionJob.source_external_id.isnot(None))
    .filter(CollectionJob.started_at > datetime.utcnow() - timedelta(days=RECENCY_WINDOW_DAYS))
    .distinct()
    .all()
)
```

That's it. No schema change, no migration.

### 2. Optional — make the window configurable

If you want the window tunable without code edits, plumb it through settings:

File: `app/core/config.py`

```python
collection_recency_window_days: int = 14
```

Then use `settings.collection_recency_window_days` in place of the constant.

## How to verify after applying

### Before/after row count comparison

In Supabase SQL Editor, run **before** applying:

```sql
SELECT COUNT(DISTINCT target_movie_id) AS subscribed_count
FROM collection_jobs
WHERE source_external_id IS NOT NULL;
```

After applying, run via the API:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/collection/scheduler/trigger-now -Method Post
```

Check the response's `summary.attempted` field. It should equal:

```sql
SELECT COUNT(DISTINCT target_movie_id) AS active_count
FROM collection_jobs
WHERE source_external_id IS NOT NULL
  AND started_at > NOW() - INTERVAL '14 days';
```

If `summary.attempted == active_count`, the filter works correctly.

### Behavioral spot-check

1. Pick a movie that was last collected >14 days ago. Trigger refresh — it should be skipped.
2. Run `run-now` on that same movie to "re-subscribe." Trigger refresh again — it should now be included.

## Reversal

Remove the added `.filter(...)` line. No data migration needed. Old (untouched) subscriptions just resume being processed.

## Trade-offs to remember

- **Less Playwright load** — desirable as movie count grows.
- **"Inactive" movies stop getting new reviews collected** — by design.
- **Re-activation requires a `run-now` call** — user-driven. Frontend should make this discoverable (e.g., "refresh now" button on movie detail).
- **Keepalive effect shrinks** — if all movies fall out of window, the cron job still runs (and queries `collection_jobs`), but the actual `SELECT ... FROM movies` traffic drops. Pair this with the existing GitHub Actions keepalive cron — do not rely on Supabase staying alive purely on this batch's activity.

## Related

- Step 7 implementation: `app/services/scheduler.py`, `app/services/collection_service.py`
- Step 7 design discussion in conversation: trade-off analysis between Option A (no filter), Option B (recency), Option C (release-date window)
