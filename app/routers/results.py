from fastapi import APIRouter, HTTPException

from app.schemas import FinalResultSchema
from app.services.result_service import get_result_by_movie_id

router = APIRouter(prefix="/movies", tags=["results"])


@router.get("/{movie_id}/review-summary", response_model=FinalResultSchema)
def read_movie_review_summary(movie_id: str):
    result = get_result_by_movie_id(movie_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result