import json
from pathlib import Path
from typing import List

from app.schemas import DatasetReviewSchema

DATASET_PATH = Path("../../data/reviews_dataset.json")


def load_all_reviews() -> List[DatasetReviewSchema]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")

    with DATASET_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [DatasetReviewSchema(**item) for item in data]


def collect_reviews(movie_id: str, limit: int | None = None) -> List[DatasetReviewSchema]:
    reviews = [review for review in load_all_reviews() if review.movie_id == movie_id]
    if limit is not None:
        reviews = reviews[:limit]
    return reviews