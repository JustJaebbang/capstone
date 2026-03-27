import json
from pathlib import Path
from typing import List, Optional

from app.schemas import FinalResultSchema

DATA_PATH = Path("data/final_results.json")


def list_results() -> List[FinalResultSchema]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [FinalResultSchema(**item) for item in data]


def get_result_by_movie_id(movie_id: str) -> Optional[FinalResultSchema]:
    for result in list_results():
        if result.movie_id == movie_id:
            return result
    return None