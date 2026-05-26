from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.collectors.movie_api_client import KOBISClient
from app.collectors.movie_mapping import CGVMovieResolver
from app.db.models.movie import Movie
from app.db.session import SessionLocal
from app.schemas import CollectedMovie

logger = logging.getLogger(__name__)

SOURCE = "kobis"


class MovieCollector(BaseCollector[CollectedMovie]):
    """KOBIS daily boxoffice -> movies table.

    Flow: boxoffice top N -> per-entry movie detail (for genre) -> upsert.
    poster_url is left NULL — KOBIS does not provide posters (toclaude2 step 2 decision).
    """

    source = SOURCE

    def __init__(self, client: KOBISClient):
        self.client = client

    def fetch(self, target_date: date | None = None, enrich_genre: bool = True) -> list[CollectedMovie]:
        raw_entries = self.client.fetch_daily_boxoffice(target_date=target_date)
        collected: list[CollectedMovie] = []

        for entry in raw_entries:
            movie_cd = entry.get("movieCd")
            if not movie_cd:
                continue

            genre = None
            if enrich_genre:
                try:
                    info = self.client.fetch_movie_info(movie_cd)
                    genre = _join_genres(info.get("genres", []))
                except Exception as exc:
                    logger.warning("genre fetch failed movieCd=%s err=%s", movie_cd, exc)

            collected.append(
                CollectedMovie(
                    source=SOURCE,
                    external_movie_id=movie_cd,
                    movie_title=entry.get("movieNm", "").strip(),
                    poster_url=None,
                    release_date=_parse_kobis_date(entry.get("openDt")),
                    genre=genre,
                )
            )

        return collected

    def save(self, items: list[CollectedMovie]) -> int:
        if not items:
            return 0

        db: Session = SessionLocal()
        inserted = 0
        try:
            for item in items:
                movie_id = _build_movie_id(item.source, item.external_movie_id)
                existing = db.get(Movie, movie_id)
                if existing is None:
                    db.add(
                        Movie(
                            movie_id=movie_id,
                            movie_title=item.movie_title,
                            release_year=item.release_date.year if item.release_date else None,
                            release_date=item.release_date,
                            poster_url=item.poster_url,
                            genre=item.genre,
                            source=item.source,
                        )
                    )
                    inserted += 1
                else:
                    existing.movie_title = item.movie_title or existing.movie_title
                    if item.release_date:
                        existing.release_date = item.release_date
                        existing.release_year = item.release_date.year
                    if item.poster_url:
                        existing.poster_url = item.poster_url
                    if item.genre:
                        existing.genre = item.genre
                    existing.updated_at = datetime.utcnow()
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        return inserted

    @staticmethod
    def resolve_cgv_codes(movie_ids: list[str] | None = None,
                          only_missing: bool = True,
                          debug_dump_dir: str | None = None,
                          headless: bool = True) -> dict[str, int]:
        """Backfill cgv_movie_code for movies that don't have one yet.

        Args:
            movie_ids: restrict to these movie_ids (e.g., newly inserted).
                       None = scan all movies in DB.
            only_missing: skip movies that already have cgv_movie_code set.
            debug_dump_dir: on failure to find hits, save screenshot + HTML here.
            headless: set False to open visible browser (manual debugging).

        Returns counts: { 'attempted': N, 'resolved': M, 'unresolved': K }.

        Heavy: spins up Playwright. Run in batch context, not per-request.
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Movie)
            if movie_ids is not None:
                query = query.filter(Movie.movie_id.in_(movie_ids))
            if only_missing:
                query = query.filter(Movie.cgv_movie_code.is_(None))
            movies = query.all()
        finally:
            db.close()

        if not movies:
            logger.info("no movies needing CGV code resolution")
            return {"attempted": 0, "resolved": 0, "unresolved": 0}

        logger.info("resolving CGV codes for %d movie(s)", len(movies))
        summary = {"attempted": len(movies), "resolved": 0, "unresolved": 0}

        with CGVMovieResolver(headless=headless, debug_dump_dir=debug_dump_dir) as resolver:
            for movie in movies:
                year = movie.release_year
                if year is None and movie.release_date:
                    year = movie.release_date.year
                try:
                    hit = resolver.resolve(movie.movie_title, year)
                except Exception:
                    logger.exception("resolver crashed for movie_id=%s", movie.movie_id)
                    hit = None

                if hit is None:
                    summary["unresolved"] += 1
                    continue

                # Persist back. Open a short-lived session per movie so a
                # later crash doesn't lose earlier progress.
                db_w: Session = SessionLocal()
                try:
                    target = db_w.get(Movie, movie.movie_id)
                    if target is not None:
                        target.cgv_movie_code = hit.code
                        if hit.poster_url and not target.poster_url:
                            target.poster_url = hit.poster_url
                        target.updated_at = datetime.utcnow()
                        db_w.commit()
                        summary["resolved"] += 1
                except Exception:
                    db_w.rollback()
                    logger.exception("failed to persist code for %s", movie.movie_id)
                    summary["unresolved"] += 1
                finally:
                    db_w.close()

        logger.info("CGV code resolution finished: %s", summary)
        return summary


def _build_movie_id(source: str, external_id: str) -> str:
    return f"{source}_{external_id}"


def _parse_kobis_date(raw: Any) -> date | None:
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw or raw == " ":
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def _join_genres(genres_field: list[dict[str, Any]]) -> str | None:
    names = [g.get("genreNm", "").strip() for g in genres_field if g.get("genreNm")]
    names = [n for n in names if n]
    return ",".join(names) if names else None
