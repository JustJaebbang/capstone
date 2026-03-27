from fastapi import APIRouter

from app.schemas import MovieSchema
from app.services.movie_service import get_movies

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[MovieSchema])
def read_movies():
    return get_movies()