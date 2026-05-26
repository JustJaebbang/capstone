"""Backfill poster_url for movies that lack one.

KOBIS does not provide poster URLs, so MovieCollector saves poster_url=NULL.
This script re-runs the CGV resolver, which extracts the poster src from
search results, and persists it back.

Usage:
    uv run python scripts/backfill_poster_urls.py                 # only NULL posters
    uv run python scripts/backfill_poster_urls.py --all           # re-fetch every movie
    uv run python scripts/backfill_poster_urls.py --movie-id kobis_20252402

Heavy — Playwright Chromium per movie, ~5s each.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session  # noqa: E402

from app.collectors.movie_mapping import CGVMovieResolver  # noqa: E402
from app.db.models.movie import Movie  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("backfill_poster_urls")


def _pick_movies(movie_id: str | None, refetch_all: bool) -> list[Movie]:
    db: Session = SessionLocal()
    try:
        query = db.query(Movie)
        if movie_id:
            query = query.filter(Movie.movie_id == movie_id)
        elif not refetch_all:
            query = query.filter(Movie.poster_url.is_(None))
        return query.order_by(Movie.movie_id).all()
    finally:
        db.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Backfill poster_url for movies")
    parser.add_argument("--all", action="store_true", help="Re-fetch poster even if already set")
    parser.add_argument("--movie-id", default=None, help="Backfill only this single movie_id")
    parser.add_argument("--debug-dump-dir", default=None)
    parser.add_argument("--no-headless", dest="headless", action="store_false", default=True)
    args = parser.parse_args(argv[1:])

    movies = _pick_movies(args.movie_id, args.all)
    if not movies:
        logger.info("no movies need poster backfill")
        return 0

    logger.info("backfilling poster_url for %d movie(s)", len(movies))
    summary = {"attempted": len(movies), "resolved": 0, "unresolved": 0}

    with CGVMovieResolver(headless=args.headless, debug_dump_dir=args.debug_dump_dir) as resolver:
        for movie in movies:
            year = movie.release_year or (movie.release_date.year if movie.release_date else None)
            try:
                hit = resolver.resolve(movie.movie_title, year)
            except Exception:
                logger.exception("resolver crashed for movie_id=%s", movie.movie_id)
                hit = None

            if hit is None or not hit.poster_url:
                summary["unresolved"] += 1
                continue

            db_w: Session = SessionLocal()
            try:
                target = db_w.get(Movie, movie.movie_id)
                if target is not None:
                    target.poster_url = hit.poster_url
                    if not target.cgv_movie_code:
                        target.cgv_movie_code = hit.code
                    target.updated_at = datetime.utcnow()
                    db_w.commit()
                    summary["resolved"] += 1
                    logger.info("  %s -> %s", movie.movie_id, hit.poster_url)
            except Exception:
                db_w.rollback()
                logger.exception("failed to persist for %s", movie.movie_id)
                summary["unresolved"] += 1
            finally:
                db_w.close()

    logger.info("done: %s", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
