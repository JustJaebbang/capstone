"""Orchestrator for the collector layer.

Responsibility (per toclaude2 §"Collector 역할"):
- Owns the collection_jobs lifecycle (queued/running/completed/failed).
- Dispatches to the appropriate source-specific collector (currently CGV only).
- Catches collector exceptions and records them on the job — never raises
  past the service boundary for the happy path; only ValueErrors for invalid
  input bubble up to the router as 4xx.

This service MUST NOT call LLM / clustering / final-result modules.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.collectors.selected_review_collector import CGVReviewClient, CGVReviewCollector
from app.db.models.collection_job import CollectionJob
from app.db.models.movie import Movie
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = {"cgv"}


class MovieNotFoundError(ValueError):
    pass


class UnsupportedSourceError(ValueError):
    pass


PREVIEW_TARGET_COUNT = 50


def run_collection_now(
    movie_id: str,
    cgv_movie_code: Optional[str] = None,
    source: str = "cgv",
    mode: str = "run_now",
    depth: str = "preview",
    cgv_client: Optional[CGVReviewClient] = None,
) -> CollectionJob:
    """Synchronously collect reviews for one movie and record a job row.

    `mode` distinguishes 'run_now' (API-triggered) from 'scheduled' (cron).
    Used for audit/dashboard only — does NOT affect execution path.

    `depth` controls how deep CGV is scrolled:
      - 'preview': stop at ~50 reviews (~30-60s). Default for user-facing run-now.
      - 'full':    scroll until exhausted (5-15 min). Used by nightly batch.

    Returns the resulting CollectionJob (status either 'completed' or
    'failed'). Raises MovieNotFoundError / UnsupportedSourceError / ValueError
    for input validation failures — caller maps these to 404/400.
    """
    if source not in SUPPORTED_SOURCES:
        raise UnsupportedSourceError(
            f"source '{source}' is not supported. Supported: {sorted(SUPPORTED_SOURCES)}"
        )
    if depth not in ("preview", "full"):
        raise ValueError(f"depth must be 'preview' or 'full', got: {depth!r}")

    db: Session = SessionLocal()
    try:
        movie = db.get(Movie, movie_id)
        if movie is None:
            raise MovieNotFoundError(f"movie_id '{movie_id}' not found in movies table")

        # If caller didn't pass cgv_movie_code, look it up on the movie row.
        # The resolver is run at ingest (collect_movies.py) or via the
        # resolve_cgv_codes.py backfill script — never inline here.
        if source == "cgv" and not cgv_movie_code:
            cgv_movie_code = movie.cgv_movie_code
        if source == "cgv" and not cgv_movie_code:
            raise ValueError(
                f"cgv_movie_code is missing for movie_id '{movie_id}' — "
                f"run scripts/resolve_cgv_codes.py to populate it"
            )

        job = CollectionJob(
            collection_job_id=_new_job_id(),
            source=source,
            mode=mode,
            target_movie_id=movie_id,
            source_external_id=cgv_movie_code,
            status="running",
            started_at=datetime.utcnow(),
            total_fetched=0,
            total_inserted=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            # depth drives both: scroll-driven path (always full_pagination=True
            # now) and a target-count cap for preview. 'full' lifts the cap to
            # chase the per-movie Throughput KPI.
            target_count = None if depth == "full" else PREVIEW_TARGET_COUNT
            items = _run_source_collector(
                source, movie_id, cgv_movie_code,
                full_pagination=True, target_count=target_count,
                cgv_client=cgv_client,
            )
            inserted = _save_via_source_collector(source, items)
            job.status = "completed"
            job.total_fetched = len(items)
            job.total_inserted = inserted
            logger.info(
                "collection job %s [mode=%s depth=%s] completed: fetched=%d inserted=%d",
                job.collection_job_id, mode, depth, len(items), inserted,
            )
        except Exception as exc:
            logger.exception("collection job %s failed", job.collection_job_id)
            job.status = "failed"
            job.error_message = str(exc)[:1000]
        finally:
            job.finished_at = datetime.utcnow()
            db.commit()
            db.refresh(job)

        return job
    finally:
        db.close()


def subscribe_to_movie(
    movie_id: str,
    cgv_movie_code: Optional[str] = None,
    source: str = "cgv",
) -> dict:
    """Register a movie for nightly batch processing — does NOT collect now.

    The nightly batch (`refresh_all_subscribed_movies`) already iterates
    distinct (target_movie_id, source, source_external_id) from
    collection_jobs, so the act of inserting one queued row here is
    sufficient to "subscribe" the movie.

    Idempotent: if a subscription already exists for (movie, source, code),
    returns the existing row with `already_subscribed=True`.

    Returns a dict with the SubscribeResponse fields except `next_batch_at`
    (router fills that from the scheduler).
    """
    if source not in SUPPORTED_SOURCES:
        raise UnsupportedSourceError(
            f"source '{source}' is not supported. Supported: {sorted(SUPPORTED_SOURCES)}"
        )

    db: Session = SessionLocal()
    try:
        movie = db.get(Movie, movie_id)
        if movie is None:
            raise MovieNotFoundError(f"movie_id '{movie_id}' not found in movies table")

        # Resolve cgv_movie_code: explicit > DB cache
        if source == "cgv" and not cgv_movie_code:
            cgv_movie_code = movie.cgv_movie_code
        if source == "cgv" and not cgv_movie_code:
            raise ValueError(
                f"cgv_movie_code is missing for movie_id '{movie_id}' — "
                f"run scripts/resolve_cgv_codes.py to populate it"
            )

        existing = (
            db.query(CollectionJob)
            .filter(
                CollectionJob.target_movie_id == movie_id,
                CollectionJob.source == source,
                CollectionJob.source_external_id == cgv_movie_code,
            )
            .order_by(CollectionJob.started_at.desc())
            .first()
        )
        if existing is not None:
            logger.info(
                "subscribe idempotent — existing row %s for movie %s",
                existing.collection_job_id, movie_id,
            )
            return {
                "subscribed": True,
                "movie_id": movie_id,
                "source": source,
                "cgv_movie_code": cgv_movie_code,
                "already_subscribed": True,
                "collection_job_id": existing.collection_job_id,
            }

        job = CollectionJob(
            collection_job_id=_new_job_id(),
            source=source,
            mode="scheduled",
            target_movie_id=movie_id,
            source_external_id=cgv_movie_code,
            status="queued",
            started_at=datetime.utcnow(),
            total_fetched=0,
            total_inserted=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(
            "subscribed movie_id=%s source=%s code=%s job_id=%s",
            movie_id, source, cgv_movie_code, job.collection_job_id,
        )
        return {
            "subscribed": True,
            "movie_id": movie_id,
            "source": source,
            "cgv_movie_code": cgv_movie_code,
            "already_subscribed": False,
            "collection_job_id": job.collection_job_id,
        }
    finally:
        db.close()


def refresh_all_subscribed_movies(
    mode: str = "scheduled",
    run_analysis: bool = True,
    run_movie_collection: bool = True,
) -> dict[str, int]:
    """Scheduled batch entry point.

    Steps:
    0. (run_movie_collection=True) Pull yesterday's KOBIS boxoffice into the
       movies table and auto-resolve CGV codes for any new entries. New movies
       become visible in /movies but are NOT auto-subscribed — users must
       explicitly subscribe (or run-now) to start collecting reviews for them.
    1. Iterate distinct (target_movie_id, source, source_external_id) tuples
       from collection_jobs — movies users have previously subscribed to.
       Re-collect reviews for each (full depth, smart incremental early-exit).
    2. If new reviews arrived AND `run_analysis=True`, run the full
       analysis pipeline (LLM -> cluster -> final) for that movie.

    Failures at any stage are logged and skipped — the batch never aborts
    on one bad movie or a KOBIS outage. Returns summary counts.
    """
    summary = {
        "movies_fetched": 0,
        "movies_inserted": 0,
        "cgv_codes_resolved": 0,
        "attempted": 0,
        "completed": 0,
        "failed": 0,
        "analyzed": 0,
        "analysis_failed": 0,
        "analysis_skipped_no_new": 0,
    }

    # Step 0: KOBIS daily movie collection + CGV resolution.
    if run_movie_collection:
        movie_step = _run_daily_movie_collection()
        summary["movies_fetched"] = movie_step.get("fetched", 0)
        summary["movies_inserted"] = movie_step.get("inserted", 0)
        summary["cgv_codes_resolved"] = movie_step.get("resolved", 0)

    db: Session = SessionLocal()
    try:
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
    finally:
        db.close()

    logger.info(
        "refresh batch starting [mode=%s analyze=%s] — %d unique subscriptions",
        mode, run_analysis, len(rows),
    )

    # Share one Playwright/Chromium across all movies in this batch.
    # Saves ~2-5s per movie of browser startup (Phase 1 optimization).
    # Falls back to per-movie client only if shared one fails to start.
    shared_cgv_client: Optional[CGVReviewClient] = None
    if any(src == "cgv" for _, src, _ in rows):
        try:
            shared_cgv_client = CGVReviewClient()
            shared_cgv_client._ensure_started()
        except Exception:
            logger.exception("shared CGV client failed to start; falling back to per-movie clients")
            shared_cgv_client = None

    try:
        for movie_id, source, ext_id in rows:
            summary["attempted"] += 1
            try:
                job = run_collection_now(
                    movie_id=movie_id,
                    cgv_movie_code=ext_id,
                    source=source,
                    mode=mode,
                    depth="full",
                    cgv_client=shared_cgv_client if source == "cgv" else None,
                )
                if job.status != "completed":
                    summary["failed"] += 1
                    continue
                summary["completed"] += 1

                if not run_analysis:
                    continue
                if job.total_inserted == 0:
                    summary["analysis_skipped_no_new"] += 1
                    continue

                # Local import avoids any future circular-import risk if
                # job_service ever needs to import collection types.
                from app.services import job_service
                try:
                    job_service.run_full_pipeline(movie_id=movie_id)
                    summary["analyzed"] += 1
                except Exception:
                    logger.exception("analysis pipeline failed for movie_id=%s", movie_id)
                    summary["analysis_failed"] += 1
            except Exception:
                logger.exception("refresh failed for movie_id=%s source=%s", movie_id, source)
                summary["failed"] += 1
    finally:
        if shared_cgv_client is not None:
            try:
                shared_cgv_client.close()
            except Exception:
                logger.warning("shared CGV client close failed", exc_info=True)

    logger.info("refresh batch finished: %s", summary)
    return summary


def _run_daily_movie_collection() -> dict[str, int]:
    """Pull yesterday's KOBIS boxoffice and resolve CGV codes.

    Failures are caught and logged here — the caller should never abort
    the review-refresh stage just because KOBIS is down.

    Returns {fetched, inserted, resolved}. All zero on failure or when
    KOBIS_API_KEY is unset.
    """
    from app.core.config import settings
    if not settings.kobis_api_key:
        logger.info("daily movie collection skipped — KOBIS_API_KEY not configured")
        return {"fetched": 0, "inserted": 0, "resolved": 0}

    try:
        from app.collectors.movie_api_client import KOBISClient
        from app.collectors.movie_collector import MovieCollector

        client = KOBISClient(api_key=settings.kobis_api_key)
        collector = MovieCollector(client=client)
        items = collector.fetch()
        inserted = collector.save(items)
        new_movie_ids = [f"{it.source}_{it.external_movie_id}" for it in items]
        resolution = MovieCollector.resolve_cgv_codes(
            movie_ids=new_movie_ids, only_missing=True,
        )
        logger.info(
            "daily movie collection: fetched=%d inserted=%d cgv_resolution=%s",
            len(items), inserted, resolution,
        )
        return {
            "fetched": len(items),
            "inserted": inserted,
            "resolved": resolution.get("resolved", 0),
        }
    except Exception:
        logger.exception("daily movie collection failed — continuing with review refresh")
        return {"fetched": 0, "inserted": 0, "resolved": 0}


def _run_source_collector(source: str, movie_id: str, cgv_movie_code: Optional[str],
                          full_pagination: bool = False,
                          target_count: Optional[int] = None,
                          cgv_client: Optional[CGVReviewClient] = None):
    if source == "cgv":
        # If caller passed a shared client, inject it — collector won't close it.
        # Otherwise collector lazily creates + closes its own (run-now path).
        collector = CGVReviewCollector(client=cgv_client) if cgv_client else CGVReviewCollector()
        return collector.fetch(
            movie_id=movie_id,
            cgv_movie_code=cgv_movie_code,
            full_pagination=full_pagination,
            target_count=target_count,
        )
    raise UnsupportedSourceError(source)


def _save_via_source_collector(source: str, items) -> int:
    if source == "cgv":
        return CGVReviewCollector().save(items)
    raise UnsupportedSourceError(source)


def _new_job_id() -> str:
    return f"cjob_{uuid.uuid4().hex[:16]}"
