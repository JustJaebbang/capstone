import json
from pathlib import Path
from typing import List, Optional

from app.schemas import DatasetReviewSchema

DATASET_PATH = Path("data/reviews_dataset.json")


def load_all_reviews_from_dataset() -> List[DatasetReviewSchema]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")

    with DATASET_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [DatasetReviewSchema(**item) for item in data]


def collect_reviews_from_dataset(
    movie_id: str,
    review_limit: Optional[int] = None,
) -> List[DatasetReviewSchema]:
    reviews = [
        review
        for review in load_all_reviews_from_dataset()
        if review.movie_id == movie_id
    ]

    if review_limit is not None:
        reviews = reviews[:review_limit]

    return reviews


def collect_reviews_from_real_source(
    movie_id: str,
    review_limit: Optional[int] = None,
) -> List[DatasetReviewSchema]:
    """
    실제 크롤링 / DB / 외부 API 연결용 자리.
    지금은 아직 구현하지 않고 비워둔다.
    """
    raise NotImplementedError("real source mode is not implemented yet")


def fetch_reviews(
    movie_id: str,
    review_limit: Optional[int] = None,
    source_mode: str = "dataset",
) -> List[DatasetReviewSchema]:
    """
    source_mode에 따라 리뷰 데이터 소스를 결정한다.
    - dataset: 현재 확보한 테스트 데이터셋 사용
    - real: 향후 실제 크롤링/DB/API 사용
    """
    if source_mode == "dataset":
        return collect_reviews_from_dataset(
            movie_id=movie_id,
            review_limit=review_limit,
        )

    if source_mode == "real":
        return collect_reviews_from_real_source(
            movie_id=movie_id,
            review_limit=review_limit,
        )

    raise ValueError(f"Unsupported source_mode: {source_mode}")