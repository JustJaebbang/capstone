from app.schemas import ClusterRequestSchema, ClusterResponseSchema, PhraseItem
from app.services.clustering_service_core_aspect_phrase_llm import (
    cluster_by_core_aspect_phrase_llm,
)
from app.services.clustering_service_hdbscan import cluster_phrases_with_hdbscan
from app.services.clustering_service_kmeans import cluster_phrases_with_kmeans
from app.services.result_service import get_llm_phrases_by_job_id


def build_cluster_request_for_job(job) -> ClusterRequestSchema:
    rows = get_llm_phrases_by_job_id(job.job_id)

    if not rows:
        raise ValueError(f"LLM phrases not found in DB for job_id={job.job_id}")

    phrases = [
        PhraseItem(
            review_id=row.review_id,
            text=row.text,
            sentiment=row.sentiment,
        )
        for row in rows
    ]

    return ClusterRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        phrases=phrases,
    )


def run_cluster_module(
    payload: ClusterRequestSchema,
    mode: str = "phrase_llm",
) -> ClusterResponseSchema:
    if mode == "hdbscan":
        return cluster_phrases_with_hdbscan(payload)

    if mode == "kmeans":
        return cluster_phrases_with_kmeans(payload)

    if mode == "phrase_llm":
        # HDBSCAN groups phrases first, then GPT re-buckets each phrase into the
        # fixed core aspects (연기/스토리/...). Falls back to the raw HDBSCAN
        # result if the OpenAI client is unavailable.
        hdbscan_result = cluster_phrases_with_hdbscan(payload)
        return cluster_by_core_aspect_phrase_llm(hdbscan_result)

    raise ValueError(f"Unsupported cluster mode: {mode}")
