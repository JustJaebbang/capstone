from fastapi import APIRouter, HTTPException

from app.schemas import MovieSchema, MovieSearchResponse, ReviewTrafficResponse
from app.services.movie_service import get_movies, get_review_traffic, search_movies

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[MovieSchema])
def read_movies():
    return get_movies()


@router.get("/search", response_model=MovieSearchResponse)
def search_movies_endpoint(q: str = "", limit: int = 20):
    """제목 검색(대소문자·공백 무시 부분일치). 빈 q는 빈 결과."""
    return search_movies(q, limit=limit)


@router.get("/{movie_id}/review-traffic", response_model=ReviewTrafficResponse)
def read_review_traffic(movie_id: str, granularity: str = "day"):
    """영화의 리뷰 작성일 기준 시계열(일/주별 리뷰 수). 그래프용."""
    try:
        return get_review_traffic(movie_id, granularity=granularity)
    except ValueError as e:
        # 알 수 없는 granularity는 400, 없는 movie_id는 404로 구분.
        if "granularity" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
