from fastapi import APIRouter, HTTPException

from app.schemas import CreateBatchJobRequest, CreateBatchJobResponse, JobStatusResponse
from app.services.job_service import (
    create_job, 
    get_job, 
    run_llm_for_job, 
    run_cluster_for_job,
    run_final_for_job,
    get_opinion_group_reviews,
    get_opinion_groups,
)
from app.services.movie_service import get_movies
from app.services.cluster_service import build_cluster_request_for_job
from app.services.result_service import (
    get_llm_result_by_job_id, 
    get_cluster_result_by_job_id,
    get_final_result_by_job_id,
)


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


@router.post("/{job_id}/run-llm")
def run_batch_job(
    job_id: str,
    review_limit: int = 1000,
    source_mode: str = "dataset", 
    llm_mode: str = "rule_based", 
    ):
    """
    예시:
    POST /batch/jobs/job_001/run?review_limit=5&source_mode=dataset&llm_mode=rule_based
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:    
        result = run_llm_for_job(
            job=job,
            review_limit=review_limit,
            source_mode=source_mode, 
            llm_mode=llm_mode, 
            )
        return result
        
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/llm-result")
def get_llm_result(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result = get_llm_result_by_job_id(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="LLM result not found")

    return result


@router.post("/{job_id}/run-cluster")
def run_cluster_job(
    job_id: str,
    cluster_mode: str = "hdbscan",
):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        result = run_cluster_for_job(
            job=job,
            cluster_mode=cluster_mode,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/cluster-result")
def get_cluster_result(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result = get_cluster_result_by_job_id(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cluster result not found")

    return result


@router.post("/{job_id}/build-final")
def build_final(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        result = run_final_for_job(job)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{job_id}/final-result")
def get_final_result(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result = get_final_result_by_job_id(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Final result not found")

    return result


@router.get("/{job_id}/opinion-groups")
def get_opinion_groups_api(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        result = get_opinion_groups(job)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/opinion-groups/{cluster_id}/reviews")
def get_opinion_group_reviews_api(
    job_id: str,
    cluster_id: str,
    page: int = 1,
    page_size: int = 20,
):
    
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        result = get_opinion_group_reviews(
            job,
            cluster_id,
            page=page,
            page_size=page_size,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))