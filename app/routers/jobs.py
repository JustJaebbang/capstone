from fastapi import APIRouter, HTTPException

from app.schemas import CreateBatchJobRequest, CreateBatchJobResponse, JobStatusResponse
from app.services.job_service import create_job, get_job
from app.services.movie_service import get_movies
from app.services.pipeline_service import run_llm_pipeline_for_job


router = APIRouter(prefix="/batch/jobs", tags=["jobs"])


@router.post("", response_model=CreateBatchJobResponse)
def create_batch_job(payload: CreateBatchJobRequest):
    movies = get_movies()
    target_movie = next((m for m in movies if m.movie_id == payload.movie_id), None)

    if target_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    job = create_job(payload, movie_title=target_movie.movie_title)
    return CreateBatchJobResponse(job_id=job.job_id, status=job.status)


@router.get("/{job_id}", response_model=JobStatusResponse)
def read_job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job.job_id, status=job.status)

@router.post("/{job_id}/run")
def run_batch_job(job_id: str):
    try:
        result = run_llm_pipeline_for_job(job_id=job_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e