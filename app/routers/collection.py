"""HTTP surface for the collector layer.

Endpoints:
- POST /collection/reviews/run-now — synchronously trigger one-shot collection
  for a given movie_id. The backend resolves cgv_movie_code internally from
  the movies table. Returns the resulting collection_job row.

Future endpoints (Step 7+): GET /collection/jobs/{id}, GET /collection/jobs
(listing).
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.db.models.collection_job import CollectionJob
from app.schemas import (
    CollectionJobResponse,
    CollectionRunRequest,
    SubscribeRequest,
    SubscribeResponse,
)
from app.services import collection_service, job_service, scheduler
from app.services.collection_service import (
    MovieNotFoundError,
    UnsupportedSourceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collection", tags=["collection"])


@router.post("/reviews/run-now", response_model=CollectionJobResponse)
def run_now(request: CollectionRunRequest) -> CollectionJobResponse:
    try:
        job = collection_service.run_collection_now(
            movie_id=request.movie_id,
            source=request.source,
            depth=request.depth,
        )
    except MovieNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (UnsupportedSourceError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    analysis_job_id: str | None = None
    analysis_status: str | None = "not_requested"

    if request.run_analysis:
        if job.status != "completed":
            analysis_status = "skipped_collection_failed"
        elif job.total_inserted == 0:
            analysis_status = "skipped_no_new"
        else:
            try:
                analysis_job = job_service.run_full_pipeline(movie_id=request.movie_id)
                analysis_job_id = analysis_job.job_id
                analysis_status = "completed"
            except Exception as exc:
                logger.exception("analysis pipeline failed after run-now")
                analysis_status = f"failed: {str(exc)[:200]}"

    return _to_response(job, analysis_job_id=analysis_job_id, analysis_status=analysis_status)


@router.post("/subscribe", response_model=SubscribeResponse)
def subscribe(request: SubscribeRequest) -> SubscribeResponse:
    """Register a movie for nightly batch processing — returns immediately.

    Unlike run-now (synchronous, 30~60s wait), this endpoint just records
    the subscription intent in collection_jobs and returns. The next nightly
    batch will pick it up via refresh_all_subscribed_movies.

    Idempotent: re-subscribing the same movie returns the existing row.
    """
    try:
        result = collection_service.subscribe_to_movie(
            movie_id=request.movie_id,
            source=request.source,
        )
    except MovieNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (UnsupportedSourceError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return SubscribeResponse(
        **result,
        next_batch_at=scheduler.get_next_run_time(),
    )


@router.post("/scheduler/trigger-now")
def trigger_scheduler_now() -> dict:
    """Run the nightly refresh batch immediately, ignoring schedule.

    Equivalent to what the cron does at 03:00. Returns batch summary.
    Useful for verifying the batch flow without waiting for the next cron tick.
    """
    summary = scheduler.trigger_refresh_now()
    return {"status": "completed", "summary": summary}


@router.get("/scheduler/status")
def scheduler_status() -> dict:
    """Inspection — next scheduled refresh time."""
    return {
        "next_run_time": scheduler.get_next_run_time(),
    }


def _to_response(
    job: CollectionJob,
    analysis_job_id: str | None = None,
    analysis_status: str | None = None,
) -> CollectionJobResponse:
    return CollectionJobResponse(
        collection_job_id=job.collection_job_id,
        source=job.source,
        mode=job.mode,
        target_movie_id=job.target_movie_id,
        source_external_id=job.source_external_id,
        status=job.status,
        started_at=job.started_at,
        finished_at=job.finished_at,
        total_fetched=job.total_fetched,
        total_inserted=job.total_inserted,
        error_message=job.error_message,
        analysis_job_id=analysis_job_id,
        analysis_status=analysis_status,
    )
