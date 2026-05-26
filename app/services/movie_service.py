from app.db.models.movie import Movie
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
