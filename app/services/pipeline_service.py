from app.schemas import LLMRequestSchema, ReviewItem
from app.services.job_service import get_job, update_job_status
from app.services.review_service import collect_reviews
from app.services.llm_service import (
    LLM_MODE,
    extract_key_phrases_by_mode,
)


def build_llm_request(job) -> LLMRequestSchema:
    dataset_reviews = collect_reviews(movie_id=job.movie_id, limit=150)

    reviews = [
        ReviewItem(
            review_id=review.review_id,
            text=review.text,
        )
        for review in dataset_reviews
    ]

    return LLMRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        target_date=job.target_date,
        reviews=reviews,
    )


def run_llm_pipeline_for_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise ValueError(f"Job not found: {job_id}")

    update_job_status(job_id, "collecting_reviews")
    llm_request = build_llm_request(job)

    update_job_status(job_id, "llm_processing")
    payload = llm_request.model_dump(mode="json")
    print(
        f"[LLM] pipeline start: job_id={job_id}, mode={LLM_MODE}, review_count={len(llm_request.reviews)}",
        flush=True,
    )

    llm_result = extract_key_phrases_by_mode(payload, mode=LLM_MODE)
    print(
        f"[LLM] pipeline done: job_id={job_id}, mode={LLM_MODE}, result_count={len(llm_result.get('results', []))}",
        flush=True,
    )

    update_job_status(job_id, "completed")
    return llm_result