from fastapi import APIRouter, HTTPException

from app.schemas import ClusterResponseSchema
from app.services.job_service import get_job, update_job_status
from app.services.cluster_service import build_cluster_request_for_job
from app.services.clustering_service_hdbscan import HDBSCANClusteringService
from app.services.clustering_service_kmeans import KMeansClusteringService

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.post("/{job_id}", response_model=ClusterResponseSchema)
def run_cluster_by_job_id(job_id: str, algorithm: str = "hdbscan"):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        request = build_cluster_request_for_job(job)

        if algorithm == "hdbscan":
            service = HDBSCANClusteringService()
        elif algorithm == "kmeans":
            service = KMeansClusteringService()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        result = service.cluster(request)

        update_job_status(job_id, "completed")
        return ClusterResponseSchema.model_validate(result)

    except ValueError as e:
        update_job_status(job_id, "failed")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        update_job_status(job_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))