from app.schemas import ClusterResponseSchema
from app.services.pipeline_service import build_cluster_request_for_job
from app.services.result_service import save_cluster_result
from app.services.clustering_service_hdbscan import run_hdbscan_clustering
from app.services.clustering_service_kmeans import run_kmeans_clustering
from app.services.job_service import update_job_status


def run_clustering(phrases, algorithm: str = "hdbscan") -> list[dict]:
    if algorithm == "hdbscan":
        return run_hdbscan_clustering(phrases)

    if algorithm == "kmeans":
        return run_kmeans_clustering(phrases)

    raise ValueError(f"Unsupported algorithm: {algorithm}")


def cluster_phrases_for_job(job, algorithm: str = "hdbscan") -> dict:
    # 저장된 llm_results -> cluster request 생성
    cluster_request = build_cluster_request_for_job(job)

    if not cluster_request.phrases:
        raise ValueError(f"No phrases found for job_id={job.job_id}")

    update_job_status(job.job_id, "clustering")

    clusters = run_clustering(cluster_request.phrases, algorithm=algorithm)

    result = ClusterResponseSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        clusters=clusters,
    )

    save_cluster_result(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=result.model_dump(mode="json"),
    )

    update_job_status(job.job_id, "completed")

    return result.model_dump(mode="json")