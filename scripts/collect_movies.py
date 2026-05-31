"""Manual KOBIS movie collection runner.

Usage:
    uv run python scripts/collect_movies.py                  # yesterday's boxoffice
    uv run python scripts/collect_movies.py 2026-05-09       # specific date

Reads KOBIS_API_KEY from .env. Writes to Supabase via app.db.session.
"""
from __future__ import annotations

import logging
import sys
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.collectors.movie_api_client import KOBISClient  # noqa: E402
from app.collectors.movie_collector import MovieCollector  # noqa: E402
from app.core.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("collect_movies")


def _parse_target_date(argv: list[str]) -> date | None:
    if len(argv) < 2:
        return None
    try:
        return datetime.strptime(argv[1], "%Y-%m-%d").date()
    except ValueError:
        logger.error("invalid date format (expected YYYY-MM-DD): %s", argv[1])
        sys.exit(2)


def main(argv: list[str]) -> int:
    if not settings.kobis_api_key:
        logger.error("KOBIS_API_KEY is not set in .env")
        return 1

    target_date = _parse_target_date(argv)
    client = KOBISClient(api_key=settings.kobis_api_key)
    collector = MovieCollector(client=client)

    logger.info("fetching boxoffice target_date=%s", target_date or "(yesterday)")
    items = collector.fetch(target_date=target_date)
    logger.info("fetched %d movies", len(items))
    for it in items:
        logger.info("  - %s (%s) [%s] genre=%s", it.movie_title, it.external_movie_id, it.release_date, it.genre)

    inserted = collector.save(items)
    logger.info("inserted %d new movies (others updated or unchanged)", inserted)

    # Auto-resolve CGV codes for the just-collected movies. Lets the frontend
    # send only `movie_id` to /collection/reviews/run-now without users
    # needing to know CGV's internal code.
    new_movie_ids = [f"{it.source}_{it.external_movie_id}" for it in items]
    logger.info("starting CGV code resolution for %d movies", len(new_movie_ids))
    resolution = MovieCollector.resolve_cgv_codes(movie_ids=new_movie_ids, only_missing=True)
    logger.info("CGV resolution summary: %s", resolution)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
