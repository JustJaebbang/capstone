import json
from pathlib import Path
from typing import List

from app.schemas import MovieSchema

DATA_PATH = Path("data/movies.json")


def get_movies() -> List[MovieSchema]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [MovieSchema(**item) for item in data]


def get_active_movies() -> List[MovieSchema]:
    return [movie for movie in get_movies() if movie.is_active]