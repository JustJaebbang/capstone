from app.schemas import ClusterRequestSchema, ClusterResponseSchema, PhraseItem
from app.services.result_service import get_llm_result_by_job_id
from app.services.clustering_service_hdbscan import cluster_phrases_with_hdbscan
from app.services.clustering_service_kmeans import cluster_phrases_with_kmeans

def build_cluster_request_from_llm_result(job, llm_result: dict) -> ClusterRequestSchema:
    phrases = []

    for result_item in llm_result["results"]:
        review_id = result_item["review_id"]

        for phrase in result_item["phrases"]:
            phrases.append(
                PhraseItem(
                    review_id=review_id,
                    text=phrase["text"],
                    sentiment=phrase["sentiment"],
                )
            )

    return ClusterRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        phrases=phrases,
    )


def build_cluster_request_for_job(job) -> ClusterRequestSchema:
    llm_saved = get_llm_result_by_job_id(job.job_id)

    if llm_saved is None:
        raise ValueError(f"LLM result not found for job_id={job.job_id}")

    llm_result = llm_saved

    return build_cluster_request_from_llm_result(
        job=job,
        llm_result=llm_result,
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