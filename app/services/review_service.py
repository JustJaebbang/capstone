from app.db.models.review import Review
from app.db.session import SessionLocal
from app.schemas import ReviewItem


def fetch_reviews(
    movie_id: str,
    review_limit: int = 50,
    source_mode: str = "dataset",
) -> list[ReviewItem]:
    db = SessionLocal()

    try:
        query = (
            db.query(Review)
            .filter(Review.movie_id == movie_id)
            .order_by(Review.review_id)
        )

        if review_limit is not None:
            query = query.limit(review_limit)

        reviews = query.all()

        return [
            ReviewItem(
                review_id=review.review_id,
                text=review.text,
            )
            for review in reviews
        ]

    finally:
        db.close()
