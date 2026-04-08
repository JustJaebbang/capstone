from fastapi import APIRouter

from app.schemas import ClusterRequestSchema, ClusterResponseSchema
from app.services.cluster_service import run_cluster_module

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.post("/run", response_model=ClusterResponseSchema)
def run_cluster_api(
    payload: ClusterRequestSchema,
    algorithm: str = "hdbscan",
) -> ClusterResponseSchema:
    result = run_cluster_module(payload, mode=algorithm)
    return result