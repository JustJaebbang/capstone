from fastapi import APIRouter, HTTPException

from app.services.review_service import fetch_reviews

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/reviews/{movie_id}")
def preview_reviews(
    movie_id: str,
    review_limit: int = 5,
    source_mode: str = "dataset",
):
    try:
        reviews = fetch_reviews(
            movie_id=movie_id,
            review_limit=review_limit,
            source_mode=source_mode,
        )
        return reviews
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))