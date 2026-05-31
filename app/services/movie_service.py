from datetime import date, timedelta

from app.db.models.movie import Movie
from app.db.models import Review
from app.db.session import SessionLocal


def get_movies() -> list[dict]:
    db = SessionLocal()

    try:
        movies = db.query(Movie).order_by(Movie.movie_id).all()

        return [
            {
                "movie_id": movie.movie_id,
                "movie_title": movie.movie_title,
                "release_year": movie.release_year,
                "source": movie.source,
                "registered_at": movie.registered_at,
                "updated_at": movie.updated_at,
            }
            for movie in movies
        ]

    finally:
        db.close()


def _week_start(d: date) -> date:
    """해당 날짜가 속한 주의 월요일."""
    return d - timedelta(days=d.weekday())


def get_review_traffic(movie_id: str, granularity: str = "day") -> dict:
    """영화의 리뷰 작성일(written_at) 기준 시계열 트래픽.

    written_at이 있는 전체 리뷰를 일/주 버킷으로 집계하고, min~max 사이
    빈 버킷은 count=0으로 채워 연속된 그래프 데이터를 만든다.
    movie_id가 movies 테이블에 없으면 ValueError.
    """
    if granularity not in ("day", "week"):
        raise ValueError(f"Unsupported granularity: {granularity}")

    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).one_or_none()
        if movie is None:
            raise ValueError(f"movie_id '{movie_id}' not found in movies table")

        rows = (
            db.query(Review.written_at)
            .filter(Review.movie_id == movie_id, Review.written_at.isnot(None))
            .all()
        )

        counts: dict[date, int] = {}
        for (written_at,) in rows:
            bucket = written_at.date()
            if granularity == "week":
                bucket = _week_start(bucket)
            counts[bucket] = counts.get(bucket, 0) + 1

        points = _fill_gaps(counts, granularity)

        return {
            "movie_id": movie.movie_id,
            "movie_title": movie.movie_title,
            "granularity": granularity,
            "total_reviews": sum(counts.values()),
            "points": points,
        }
    finally:
        db.close()


def _fill_gaps(counts: dict[date, int], granularity: str) -> list[dict]:
    if not counts:
        return []

    step = timedelta(days=1 if granularity == "day" else 7)
    cursor, end = min(counts), max(counts)

    points = []
    while cursor <= end:
        points.append({"date": cursor, "count": counts.get(cursor, 0)})
        cursor += step
    return points
