from datetime import datetime
from typing import List, Optional

from sqlalchemy import func

from app.db.models.batch_job import BatchJob
from app.db.models.movie import Movie
from app.db.models.movie_summary import MovieSummary
from app.db.models.opinion_group import OpinionGroup
from app.db.models.review import Review
from app.db.session import SessionLocal

TOP_KEYWORDS_LIMIT = 3
RECENT_JOBS_LIMIT = 5


def _latest_completed_job_id_by_movie(db) -> dict[str, str]:
    rows = (
        db.query(
            BatchJob.movie_id,
            BatchJob.job_id,
            BatchJob.finished_at,
        )
        .filter(BatchJob.status == "completed")
        .order_by(BatchJob.movie_id, BatchJob.finished_at.desc())
        .all()
    )

    latest: dict[str, str] = {}
    for row in rows:
        if row.movie_id not in latest:
            latest[row.movie_id] = row.job_id
    return latest


def _review_counts_by_movie(db) -> dict[str, int]:
    rows = (
        db.query(Review.movie_id, func.count(Review.review_id))
        .group_by(Review.movie_id)
        .all()
    )
    return {movie_id: count for movie_id, count in rows}


def _top_keywords_for_job(db, job_id: str) -> List[dict]:
    groups = (
        db.query(OpinionGroup)
        .filter(OpinionGroup.job_id == job_id)
        .order_by(OpinionGroup.count.desc(), OpinionGroup.cluster_id)
        .limit(TOP_KEYWORDS_LIMIT)
        .all()
    )
    return [
        {
            "rank": idx,
            "topic": g.topic,
            "sentiment": g.sentiment,
            "label": g.label,
            "count": g.count,
        }
        for idx, g in enumerate(groups, start=1)
    ]


def get_dashboard_movies() -> dict:
    db = SessionLocal()
    try:
        movies = db.query(Movie).order_by(Movie.movie_id).all()
        summaries = {
            s.movie_id: s
            for s in db.query(MovieSummary).all()
        }
        latest_job_by_movie = _latest_completed_job_id_by_movie(db)
        review_counts = _review_counts_by_movie(db)

        items: List[dict] = []
        for movie in movies:
            summary: Optional[MovieSummary] = summaries.get(movie.movie_id)
            job_id = latest_job_by_movie.get(movie.movie_id)

            top_keywords = _top_keywords_for_job(db, job_id) if job_id else []

            items.append(
                {
                    "movie_id": movie.movie_id,
                    "movie_title": movie.movie_title,
                    "poster_url": movie.poster_url,
                    "genre": movie.genre,
                    "release_year": movie.release_year,
                    "release_date": movie.release_date,
                    "source": movie.source,
                    "total_review_count": review_counts.get(movie.movie_id, 0),
                    "sentiment_ratio": {
                        "positive_percent": summary.positive_percent if summary else 0.0,
                        "negative_percent": summary.negative_percent if summary else 0.0,
                    },
                    "top_keywords": top_keywords,
                    "latest_job_id": job_id,
                }
            )

        return {"items": items, "total_count": len(items)}
    finally:
        db.close()


def get_dashboard_summary() -> dict:
    db = SessionLocal()
    try:
        total_movies = db.query(func.count(Movie.movie_id)).scalar() or 0

        total_completed_jobs = (
            db.query(func.count(BatchJob.job_id))
            .filter(BatchJob.status == "completed")
            .scalar()
            or 0
        )

        total_reviews_analyzed = (
            db.query(func.coalesce(func.sum(MovieSummary.total_review_count), 0)).scalar()
            or 0
        )

        recent_rows = (
            db.query(BatchJob)
            .filter(BatchJob.status == "completed")
            .order_by(BatchJob.finished_at.desc().nullslast(), BatchJob.created_at.desc())
            .limit(RECENT_JOBS_LIMIT)
            .all()
        )

        recent_jobs = [
            {
                "job_id": j.job_id,
                "movie_id": j.movie_id,
                "movie_title": j.movie_title,
                "status": j.status,
                "finished_at": j.finished_at,
            }
            for j in recent_rows
        ]

        return {
            "total_movies": total_movies,
            "total_completed_jobs": total_completed_jobs,
            "total_reviews_analyzed": int(total_reviews_analyzed),
            "recent_jobs": recent_jobs,
            "updated_at": datetime.utcnow(),
        }
    finally:
        db.close()
