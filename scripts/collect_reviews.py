"""Manual CGV review collection runner.

Usage:
    uv run python scripts/collect_reviews.py kobis_20239012
    uv run python scripts/collect_reviews.py kobis_20239012 --max-pages 10

Reads database_url from .env. Writes to reviews table.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import json  # noqa: E402

from app.collectors.selected_review_collector import (  # noqa: E402
    CGVReviewClient,
    CGVReviewCollector,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("collect_reviews")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Collect CGV reviews for one movie")
    parser.add_argument("movie_id", help="movies.movie_id (e.g., kobis_20239012)")
    parser.add_argument(
        "--cgv-code",
        dest="cgv_code",
        default=None,
        help="CGV internal movie code from the detail URL "
             "(e.g., 30001046 from /cnm/cgvChart/movieChart/30001046). "
             "If omitted, falls back to automated resolver (currently unreliable).",
    )
    parser.add_argument("--max-pages", type=int, default=1, help="(reserved; Playwright path captures page 1 only)")
    parser.add_argument("--page-size", type=int, default=5, help="(reserved; CGV serves ~5 per natural load)")
    parser.add_argument(
        "--dump-json",
        dest="dump_json",
        default=None,
        help="Dump the first API page's raw JSON to this path for debugging, then exit.",
    )
    parser.add_argument(
        "--debug-dump-dir",
        dest="debug_dump_dir",
        default=None,
        help="On failure, save Playwright page screenshot + HTML to this dir.",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        default=True,
        help="Run Chromium with UI (for manual debugging of anti-bot behavior).",
    )
    args = parser.parse_args(argv[1:])

    if args.dump_json:
        if not args.cgv_code:
            logger.error("--dump-json requires --cgv-code")
            return 2
        logger.info("dumping CGV review API JSON for cgv_code=%s", args.cgv_code)
        with CGVReviewClient(
            headless=args.headless,
            debug_dump_dir=args.debug_dump_dir,
        ) as client:
            payload = client.fetch_reviews_page(args.cgv_code)
        Path(args.dump_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        items = payload.get("data", {}).get("list", []) or []
        logger.info("wrote %s (statusCode=%s, %d review items)",
                    args.dump_json, payload.get("statusCode"), len(items))
        return 0

    collector = CGVReviewCollector(
        headless=args.headless,
        debug_dump_dir=args.debug_dump_dir,
    )
    logger.info(
        "fetching reviews movie_id=%s cgv_code=%s",
        args.movie_id, args.cgv_code or "(auto)",
    )
    items = collector.fetch(
        movie_id=args.movie_id,
        cgv_movie_code=args.cgv_code,
        max_pages=args.max_pages,
        page_size=args.page_size,
    )
    logger.info("fetched %d reviews", len(items))

    if not items:
        logger.warning("no reviews fetched — check --cgv-code and CGV selectors")
        return 0

    for it in items[:3]:
        preview = it.text[:60].replace("\n", " ")
        logger.info("  - [%s] %s... (rating=%s)", it.external_review_id or "—", preview, it.rating)

    inserted = collector.save(items)
    logger.info("inserted %d new reviews (others were duplicates)", inserted)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
