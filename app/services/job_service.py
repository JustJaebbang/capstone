import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.schemas import (
    BatchJobSchema, 
    CreateBatchJobRequest, 
    LLMRequestSchema, 
    ReviewItem
)
from app.services.llm_service import extract_phrases_with_sentiment
from app.services.cluster_service import build_cluster_request_for_job, run_cluster_module
from app.services.review_service import fetch_reviews
from app.services.result_service import (
    save_llm_result, 
    save_cluster_result,
    save_final_result,
    get_llm_result_by_job_id,
    get_cluster_result_by_job_id,
)

from app.services.final_service import build_final_result

DATA_PATH = Path("data/jobs.json")


def read_jobs() -> List[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_jobs(jobs: List[dict]) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def list_jobs() -> List[BatchJobSchema]:
    return [BatchJobSchema(**job) for job in read_jobs()]


def get_job(job_id: str) -> Optional[BatchJobSchema]:
    for job in list_jobs():
        if job.job_id == job_id:
            return job
    return None


def create_job(payload: CreateBatchJobRequest, movie_title: str) -> BatchJobSchema:
    jobs = read_jobs()
    new_job = BatchJobSchema(
        job_id=f"job_{len(jobs)+1:03d}",
        movie_id=payload.movie_id,
        movie_title=movie_title,
        target_date=payload.target_date,
        status="queued",
        created_at=datetime.now(),
        started_at=None,
        finished_at=None,
    )
    jobs.append(new_job.model_dump(mode="json"))
    write_jobs(jobs)
    return new_job


def update_job_status(job_id: str, new_status: str) -> None:
    jobs = read_jobs()
    updated = False

    for job in jobs:
        if job["job_id"] == job_id:
            job["status"] = new_status

            if new_status != "queued" and job["started_at"] is None:
                job["started_at"] = datetime.now().isoformat()

            if new_status in ["completed", "failed"]:
                job["finished_at"] = datetime.now().isoformat()

            updated = True
            break

    if not updated:
        raise ValueError(f"Job not found: {job_id}")

    write_jobs(jobs)


def build_llm_request(
    job, 
    review_limit: int = 50, 
    source_mode: str = "dataset",
    ) -> LLMRequestSchema:
    """
    리뷰 데이터 원본(dataset or real)에서 리뷰를 B -> C 요청 스키마로 변환한다.
    """
    source_reviews = fetch_reviews(
        movie_id=job.movie_id,
        review_limit=review_limit,
        source_mode=source_mode,
    )

    reviews = [
        ReviewItem(
            review_id=review.review_id,
            text=review.text,
        )
        for review in source_reviews
    ]

    return LLMRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        reviews=reviews,
    )


def run_llm_for_job(
    job, 
    review_limit: int = 50, 
    source_mode: str = "dataset", 
    llm_mode: str = "rule_based",
    ) -> dict:
    """
    dataset -> B -> C -> B 전체 실행
    """
    # 1. 데이터 소스에서 리뷰를 읽고 B → C 스키마 생성
    llm_request = build_llm_request(
        job=job, 
        review_limit=review_limit,
        source_mode=source_mode,
        )
    payload = llm_request.model_dump(mode="json")

    print(f"[Pipeline] source_mode = {source_mode}")
    print(f"[Pipeline] llm_mode = {llm_mode}")
    
    total_reviews = len(payload["reviews"])
    print(f"[Pipeline] selected reviews = {total_reviews}")

    # 2. C 호출
    llm_response = extract_phrases_with_sentiment(llm_request, mode=llm_mode)
    llm_result = llm_response.model_dump(mode="json")
    
    # 3. 입력 리뷰 수 == 출력 결과 수 검증
    input_count = len(payload["reviews"])
    output_count = len(llm_result["results"])

    if input_count != output_count:
        raise ValueError(
            f"LLM result count mismatch: input={input_count}, output={output_count}"
        )
    
    save_llm_result(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=llm_result,
    )
    print(f"[Pipeline] llm results received: {output_count}")
    print("[Pipeline] llm_results saved")
    
    return llm_result


def run_cluster_for_job(
    job,
    cluster_mode: str = "hdbscan",
) -> dict:
    cluster_request = build_cluster_request_for_job(job)

    cluster_response = run_cluster_module(cluster_request, mode=cluster_mode)
    cluster_result = cluster_response.model_dump(mode="json")

    save_cluster_result(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=cluster_result,
    )

    return cluster_result


def run_final_for_job(job) -> dict:
    llm_result = get_llm_result_by_job_id(job.job_id)
    if llm_result is None:
        raise ValueError(f"LLM result not found for job_id={job.job_id}")

    cluster_result = get_cluster_result_by_job_id(job.job_id)
    if cluster_result is None:
        raise ValueError(f"Cluster result not found for job_id={job.job_id}")

    source_reviews = fetch_reviews(
        movie_id=job.movie_id,
        review_limit=1000,
        source_mode="dataset",
    )

    source_reviews_data = [
        {
            "review_id": review.review_id,
            "text": review.text,
        }
        for review in source_reviews
    ]

    final_response = build_final_result(
        job=job,
        llm_result=llm_result,
        cluster_result=cluster_result,
        source_reviews=source_reviews_data,
    )
    
    final_result = final_response.model_dump(mode="json")

    save_final_result(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=final_result,
    )

    return final_result