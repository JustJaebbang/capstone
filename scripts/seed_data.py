import json
import sys
from pathlib import Path

from app.db.models.movie import Movie
from app.db.models.review import Review
from app.db.session import SessionLocal

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))


DATA_DIR = BASE_DIR / "data"
MOVIES_PATH = DATA_DIR / "movies.json"
REVIEWS_PATH = DATA_DIR / "reviews_dataset.json"


def seed_movies_from_movies_json(db):
    if not MOVIES_PATH.exists():
        print(f"[seed] movies.json not found: {MOVIES_PATH}")
        return 0

    with open(MOVIES_PATH, "r", encoding="utf-8") as f:
        movies = json.load(f)

    count = 0

    for item in movies:
        movie = db.get(Movie, item["movie_id"])

        if movie is None:
            movie = Movie(
                movie_id=item["movie_id"],
                movie_title=item["movie_title"],
                release_year=item.get("release_year"),
                source=item.get("source"),
            )
            db.add(movie)
        else:
            movie.movie_title = item["movie_title"]
            movie.release_year = item.get("release_year")
            movie.source = item.get("source")

        count += 1

    return count


def seed_reviews_from_reviews_json(db):
    if not REVIEWS_PATH.exists():
        print(f"[seed] reviews.json not found: {REVIEWS_PATH}")
        return 0

    with open(REVIEWS_PATH, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    count = 0

    for item in reviews:
        movie_id = item["movie_id"]

        # reviews.json에 movie 정보가 있으므로 movie가 없으면 자동 생성
        movie = db.get(Movie, movie_id)
        if movie is None:
            movie = Movie(
                movie_id=movie_id,
                movie_title=item.get("movie_title", movie_id),
                release_year=item.get("release_year"),
                source=item.get("source"),
            )
            db.add(movie)

        review = db.get(Review, item["review_id"])

        if review is None:
            review = Review(
                review_id=item["review_id"],
                movie_id=movie_id,
                text=item["text"],
                source=item.get("source"),
                is_processed=False,
            )
            db.add(review)
        else:
            review.movie_id = movie_id
            review.text = item["text"]
            review.source = item.get("source")

        count += 1

    return count


def main():
    db = SessionLocal()

    try:
        movie_count = seed_movies_from_movies_json(db)
        review_count = seed_reviews_from_reviews_json(db)

        db.commit()

        print(f"[seed] movies inserted/updated: {movie_count}")
        print(f"[seed] reviews inserted/updated: {review_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
