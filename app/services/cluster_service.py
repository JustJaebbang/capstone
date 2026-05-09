from app.schemas import ClusterRequestSchema, ClusterResponseSchema, PhraseItem
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
    mode: str = "hdbscan",
) -> ClusterResponseSchema:
    if mode == "hdbscan":
        return cluster_phrases_with_hdbscan(payload)

    if mode == "kmeans":
        return cluster_phrases_with_kmeans(payload)

    raise ValueError(f"Unsupported cluster mode: {mode}")
