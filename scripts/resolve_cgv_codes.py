"""Backfill cgv_movie_code for movies that lack one.

Usage:
    uv run python scripts/resolve_cgv_codes.py                # only NULL codes
    uv run python scripts/resolve_cgv_codes.py --all          # re-resolve everything
    uv run python scripts/resolve_cgv_codes.py --movie-id kobis_20252402  # one movie

Heavy operation — spins up Playwright Chromium. Expect ~5s per movie.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.collectors.movie_collector import MovieCollector  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("resolve_cgv_codes")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Backfill cgv_movie_code for movies")
    parser.add_argument("--all", action="store_true", help="re-resolve even movies that already have a code")
    parser.add_argument("--movie-id", default=None, help="resolve only this single movie_id")
    parser.add_argument(
        "--debug-dump-dir",
        dest="debug_dump_dir",
        default=None,
        help="Save screenshot + HTML for any movie that fails to resolve.",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=True,
        help="Open visible Chromium (manual debugging).",
    )
    args = parser.parse_args(argv[1:])

    movie_ids = [args.movie_id] if args.movie_id else None
    only_missing = not args.all

    summary = MovieCollector.resolve_cgv_codes(
        movie_ids=movie_ids,
        only_missing=only_missing,
        debug_dump_dir=args.debug_dump_dir,
        headless=args.headless,
    )
    logger.info("done: %s", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
