from fastapi import APIRouter, HTTPException

from app.services.review_service import collect_reviews

router = APIRouter(prefix="/movies", tags=["reviews"])


@router.get("/{movie_id}/reviews")
def read_reviews(movie_id: str, limit: int = 5):
    try:
        reviews = collect_reviews(movie_id=movie_id, limit=limit)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this movie")

    return reviews