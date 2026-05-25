"""CGV review collector (selected source, toclaude2 step 4).

Source selection rationale (decided in step 3):
- CGV scored 42/50 across the 5 criteria from toclaude2 §"추천 source 선택 기준"
- Decisive factor: review volume (1st-place multiplex in Korea)
- Other candidates excluded:
    * Naver: service shut down 2023-10
    * Lotte: React SPA, requires Selenium → violates "정적 HTML" principle
    * Megabox: smaller review volume

Architecture (per toclaude2 §"Collector 역할"):
- This module ONLY: external request, parsing, schema conversion, DB save.
- It MUST NOT call LLM / clustering / final-result modules.

Implementation notes (verify in step 5 with real data):
- Review listing URL pattern and HTML selectors are best-effort based on
  CGV's commonly-observed structure. If parsing yields zero reviews on a
  known-popular movie, the selectors below are the first thing to adjust.
"""
from __future__ import annotations

import hashlib
import logging
import re
import time
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from playwright.sync_api import sync_playwright
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.collectors.movie_mapping import DEFAULT_USER_AGENT, CGVMovieResolver
from app.db.models.movie import Movie
from app.db.models.review import Review
from app.db.session import SessionLocal
from app.schemas import CollectedReview

logger = logging.getLogger(__name__)

SOURCE = "cgv"

# CGV review JSON API. The CGV site is CSR + uses HMAC request signing
# (x-signature, x-timestamp) + Cloudflare bot management. A bare `requests`
# session hits 401; reverse-engineering the signing key is brittle. Instead
# we drive a real Chromium via Playwright, so CGV's own JS adds the
# signature for us, and we intercept the API response.
CGV_REVIEW_API_SEGMENT = "searchRviewRviewPageList"
CGV_DETAIL_URL_TEMPLATE = "https://cgv.co.kr/cnm/cgvChart/movieChart/{code}"

DEFAULT_NAV_TIMEOUT_MS = 30000
DEFAULT_POST_LOAD_WAIT_MS = 5000

# Patch script injected into every page before navigation. Hides the most
# obvious Playwright/automation markers that Cloudflare and CGV's own checks
# look for. Not a full stealth suite — just the common low-hanging fingerprints.
_STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
window.chrome = window.chrome || { runtime: {} };
"""


class CGVReviewClient:
    """Playwright-backed client for CGV's review API.

    Lifecycle: lazy-start one Chromium per client instance, reuse it for
    multiple movies, close on `.close()` (or context-manager exit).
    """

    def __init__(self, headless: bool = True, nav_timeout_ms: int = DEFAULT_NAV_TIMEOUT_MS,
                 post_load_wait_ms: int = DEFAULT_POST_LOAD_WAIT_MS,
                 user_agent: str = DEFAULT_USER_AGENT,
                 debug_dump_dir: Optional[str] = None):
        self.headless = headless
        self.nav_timeout_ms = nav_timeout_ms
        self.post_load_wait_ms = post_load_wait_ms
        self.user_agent = user_agent
        self.debug_dump_dir = debug_dump_dir
        self._pw = None
        self._browser = None
        self._context = None

    def __enter__(self) -> "CGVReviewClient":
        self._ensure_started()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _ensure_started(self) -> None:
        if self._pw is not None:
            return
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        self._context = self._browser.new_context(
            user_agent=self.user_agent,
            locale="ko-KR",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"},
        )
        self._context.add_init_script(_STEALTH_INIT_SCRIPT)

    def close(self) -> None:
        try:
            if self._context is not None:
                self._context.close()
            if self._browser is not None:
                self._browser.close()
        finally:
            if self._pw is not None:
                self._pw.stop()
            self._pw = None
            self._browser = None
            self._context = None

    def fetch_reviews_page(self, cgv_movie_code: str, start_row: int = 0,
                           list_count: int = 5) -> dict[str, Any]:
        """Navigate to the CGV movie page and intercept the natural review API call.

        Reviews on CGV's modern site are lazy-loaded by IntersectionObserver
        when the review section scrolls into view. So we navigate, scroll
        through the page, then wait for the API call to fire.

        Captures only the FIRST API response — fast path used by run-now for
        debug/verification. For full pagination use `fetch_all_reviews`.
        """
        self._ensure_started()
        page = self._context.new_page()
        page.set_default_timeout(self.nav_timeout_ms)

        captured: list = []

        def on_response(response):
            try:
                if CGV_REVIEW_API_SEGMENT in response.url and response.status == 200:
                    captured.append(response)
            except Exception:
                pass

        page.on("response", on_response)

        try:
            url = CGV_DETAIL_URL_TEMPLATE.format(code=cgv_movie_code)
            page.goto(url, wait_until="domcontentloaded", timeout=self.nav_timeout_ms)

            # Scroll progressively to trigger IntersectionObserver-based lazy loads
            for _ in range(6):
                page.evaluate("window.scrollBy(0, document.body.scrollHeight / 6)")
                page.wait_for_timeout(500)

            # Final wait for late-firing API calls (Cloudflare challenges, slow fetches)
            page.wait_for_timeout(self.post_load_wait_ms)

            if not captured:
                self._dump_debug(page, cgv_movie_code)
                raise RuntimeError(
                    f"CGV review API was not called during page load for movie {cgv_movie_code}. "
                    f"Check debug dump (if --debug-dump-dir was set)."
                )

            payload = captured[0].json()
            if payload.get("statusCode") != 0:
                raise RuntimeError(
                    f"CGV API non-zero status: "
                    f"{payload.get('statusCode')} {payload.get('statusMessage')}"
                )
            return payload
        finally:
            page.close()

    def fetch_all_reviews(self, cgv_movie_code: str,
                          max_scrolls: int = 2000,
                          scroll_wait_ms: int = 1000,
                          no_progress_limit: int = 2,
                          known_review_ids: Optional[set[str]] = None,
                          consecutive_all_known_limit: int = 2,
                          target_count: Optional[int] = None) -> dict[str, Any]:
        """Scroll-driven review collection — Throughput KPI path.

        First-time collection (known_review_ids empty/None):
          Scrolls until CGV stops returning new pages (no_progress_limit
          consecutive iterations with zero new API responses). max_scrolls
          (2000) is a *safety bound*, not a practical limit — caps at ~10000
          reviews per movie, well above CGV's per-movie ceiling.

        Incremental collection (known_review_ids provided from DB):
          Additionally short-circuits when `consecutive_all_known_limit`
          API responses in a row contain ONLY reviews already in DB. CGV
          returns newest-first (sortBy=01), so all-known responses signal
          we've passed the boundary between new and historical reviews.

        Preview mode (target_count set):
          Stops scrolling as soon as unique-reviews-so-far >= target_count.
          Use ~50 from run-now API to give the user a meaningful sample
          (~30-60s response) without committing to full pagination.

        Performance:
          - Preview (target_count=50): ~30-60 sec
          - First-time popular movie (3000 reviews): ~15 min
          - Daily increment (5 new): ~10 sec
          - Quiet movie (0 new): ~5 sec

        Returns same shape as fetch_reviews_page.
        """
        self._ensure_started()
        page = self._context.new_page()
        page.set_default_timeout(self.nav_timeout_ms)

        captured: list = []

        def on_response(response):
            try:
                if CGV_REVIEW_API_SEGMENT in response.url and response.status == 200:
                    captured.append(response)
            except Exception:
                pass

        page.on("response", on_response)

        # Incremental early-exit state — tracks responses we've already
        # inspected for "all known" since they arrived asynchronously
        # via the listener.
        processed_responses_idx = 0
        consecutive_all_known = 0
        unique_so_far: set[str] = set()
        early_exit = False

        def _check_incremental_exit() -> bool:
            """Returns True if we should stop scrolling due to all-known runs."""
            nonlocal processed_responses_idx, consecutive_all_known
            if not known_review_ids:
                return False
            while processed_responses_idx < len(captured):
                resp = captured[processed_responses_idx]
                processed_responses_idx += 1
                try:
                    items = resp.json().get("data", {}).get("list", []) or []
                except Exception:
                    continue
                if not items:
                    continue
                ids = [it.get("rviewNo") for it in items]
                all_known = all(rid and rid in known_review_ids for rid in ids)
                if all_known:
                    consecutive_all_known += 1
                    if consecutive_all_known >= consecutive_all_known_limit:
                        return True
                else:
                    consecutive_all_known = 0
            return False

        def _target_reached() -> bool:
            """Returns True once preview mode has accumulated target_count unique reviews."""
            if target_count is None:
                return False
            for resp in captured:
                try:
                    items = resp.json().get("data", {}).get("list", []) or []
                except Exception:
                    continue
                for item in items:
                    rid = item.get("rviewNo")
                    if rid:
                        unique_so_far.add(rid)
            return len(unique_so_far) >= target_count

        try:
            url = CGV_DETAIL_URL_TEMPLATE.format(code=cgv_movie_code)
            page.goto(url, wait_until="domcontentloaded", timeout=self.nav_timeout_ms)
            page.wait_for_timeout(self.post_load_wait_ms)

            # Initial check — first natural API response may already be all-known
            if _check_incremental_exit():
                early_exit = True
                logger.info(
                    "fetch_all_reviews movie=%s: incremental early-exit at scroll 0 "
                    "(initial response all-known)",
                    cgv_movie_code,
                )
            elif _target_reached():
                early_exit = True
                logger.info(
                    "fetch_all_reviews movie=%s: preview target=%d reached at scroll 0 "
                    "(unique=%d)",
                    cgv_movie_code, target_count, len(unique_so_far),
                )

            # Scroll loop
            last_count = len(captured)
            no_progress = 0
            scroll_i = 0
            if not early_exit:
                for scroll_i in range(max_scrolls):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(scroll_wait_ms)

                    if _check_incremental_exit():
                        early_exit = True
                        logger.info(
                            "fetch_all_reviews movie=%s: incremental early-exit "
                            "after %d scrolls (consecutive all-known)",
                            cgv_movie_code, scroll_i + 1,
                        )
                        break

                    if _target_reached():
                        early_exit = True
                        logger.info(
                            "fetch_all_reviews movie=%s: preview target=%d reached "
                            "after %d scrolls (unique=%d)",
                            cgv_movie_code, target_count, scroll_i + 1, len(unique_so_far),
                        )
                        break

                    current_count = len(captured)
                    if current_count == last_count:
                        no_progress += 1
                        if no_progress >= no_progress_limit:
                            logger.info(
                                "fetch_all_reviews movie=%s: exhausted after %d scrolls "
                                "(no new API responses for %d iterations, captured=%d)",
                                cgv_movie_code, scroll_i + 1, no_progress, current_count,
                            )
                            break
                    else:
                        no_progress = 0
                        last_count = current_count
                else:
                    logger.warning(
                        "fetch_all_reviews movie=%s: hit max_scrolls=%d (captured=%d) — "
                        "raise cap if more reviews expected",
                        cgv_movie_code, max_scrolls, len(captured),
                    )

            # Merge + dedup all captured responses
            all_items: list[dict] = []
            seen_ids: set[str] = set()
            for resp in captured:
                try:
                    payload = resp.json()
                except Exception:
                    continue
                if payload.get("statusCode") != 0:
                    continue
                for item in payload.get("data", {}).get("list", []) or []:
                    rid = item.get("rviewNo")
                    if rid and rid in seen_ids:
                        continue
                    if rid:
                        seen_ids.add(rid)
                    all_items.append(item)

            logger.info(
                "fetch_all_reviews movie=%s: %d API responses → %d unique reviews "
                "(early_exit=%s, known_ids=%d)",
                cgv_movie_code, len(captured), len(all_items),
                early_exit, len(known_review_ids) if known_review_ids else 0,
            )
            return {
                "statusCode": 0,
                "statusMessage": f"merged {len(captured)} responses",
                "data": {"list": all_items},
            }
        finally:
            page.close()

    def _dump_debug(self, page, cgv_movie_code: str) -> None:
        """On failure, save screenshot + HTML to debug_dump_dir if configured."""
        if not self.debug_dump_dir:
            return
        try:
            from pathlib import Path
            d = Path(self.debug_dump_dir)
            d.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(d / f"cgv_{cgv_movie_code}.png"), full_page=True)
            (d / f"cgv_{cgv_movie_code}.html").write_text(page.content(), encoding="utf-8")
            logger.info("debug dump saved to %s", d)
        except Exception as exc:
            logger.warning("debug dump failed: %s", exc)


class CGVReviewCollector(BaseCollector[CollectedReview]):
    """KOBIS movie_id -> CGV reviews -> reviews table.

    Dedup policy (toclaude2 §"중복 방지 정책"):
      1. UNIQUE(source, external_review_id) — DB-enforced
      2. (source, movie_id, text_hash) — app-level pre-check + index lookup
    """

    source = SOURCE

    def __init__(self, resolver: Optional[CGVMovieResolver] = None,
                 client: Optional[CGVReviewClient] = None,
                 debug_dump_dir: Optional[str] = None,
                 headless: bool = True):
        self.resolver = resolver or CGVMovieResolver()
        # Track ownership so cross-movie callers (nightly batch) can pass in
        # a shared client and we don't kill their browser between movies.
        if client is None:
            self.client = CGVReviewClient(
                headless=headless,
                debug_dump_dir=debug_dump_dir,
            )
            self._owns_client = True
        else:
            self.client = client
            self._owns_client = False

    def fetch(self, movie_id: str, cgv_movie_code: Optional[str] = None,
              max_pages: int = 1, page_size: int = 5,
              full_pagination: bool = False,
              target_count: Optional[int] = None) -> list[CollectedReview]:
        """Fetch reviews for a movie via CGV's JSON API (Playwright-driven).

        If `cgv_movie_code` is given, it's used directly (MVP path — manual
        mapping). Otherwise the (currently unreliable) CGVMovieResolver is tried.

        Modes:
        - full_pagination=False (default, legacy run-now path):
            Captures only the first natural API response (~5 reviews).
            Fast (~10s), for debug/verification only.
        - full_pagination=True, target_count=None (batch path):
            Scrolls until exhausted, merges all responses. Slow (5-15 min) but
            collects every available review. Used by nightly batch for the
            3000/day Throughput KPI.
        - full_pagination=True, target_count=N (preview path):
            Scrolls until N unique reviews accumulated or natural exhaustion,
            whichever first. ~30-60s for N=50. Used by run-now to give
            users a meaningful sample without long wait.
        """
        if not cgv_movie_code:
            title, release_year = self._lookup_movie(movie_id)
            if not title:
                logger.error("movie_id %s not found in movies table", movie_id)
                return []
            cgv_movie_code = self.resolver.resolve(title=title, release_year=release_year)
            if not cgv_movie_code:
                logger.error("could not resolve CGV code for %s (%s)", title, release_year)
                return []

        logger.info(
            "fetching CGV reviews movie_id=%s cgv_code=%s full_pagination=%s target=%s",
            movie_id, cgv_movie_code, full_pagination, target_count,
        )
        try:
            if full_pagination:
                known_ids = self._load_known_review_ids(movie_id)
                payload = self.client.fetch_all_reviews(
                    cgv_movie_code,
                    known_review_ids=known_ids,
                    target_count=target_count,
                )
            else:
                payload = self.client.fetch_reviews_page(cgv_movie_code)
        finally:
            if self._owns_client:
                self.client.close()

        raw_list = payload.get("data", {}).get("list", []) or []
        logger.info("captured %d reviews from natural page-load API call", len(raw_list))

        collected: list[CollectedReview] = []
        seen_review_ids: set[str] = set()
        for raw in raw_list:
            rview_no = raw.get("rviewNo")
            if rview_no and rview_no in seen_review_ids:
                continue
            if rview_no:
                seen_review_ids.add(rview_no)
            text = (raw.get("rviewCont") or "").strip()
            if not text:
                continue
            collected.append(
                CollectedReview(
                    source=SOURCE,
                    movie_id=movie_id,
                    external_review_id=rview_no,
                    author=raw.get("snsNcnm"),
                    rating=_parse_rating(raw.get("egScore")),
                    text=text,
                    written_at=_parse_written_at(raw.get("creDt")),
                )
            )

        return collected

    def save(self, items: list[CollectedReview]) -> int:
        if not items:
            return 0

        db: Session = SessionLocal()
        inserted = 0
        try:
            existing_hashes = self._load_existing_hashes(db, items)
            for item in items:
                text_hash = compute_text_hash(item.text)
                if (item.source, item.movie_id, text_hash) in existing_hashes:
                    continue  # 2-차 dedup (text_hash)

                review_id = _build_review_id(item.source, item.external_review_id,
                                             item.movie_id, text_hash)
                review = Review(
                    review_id=review_id,
                    movie_id=item.movie_id,
                    text=item.text,
                    source=item.source,
                    external_review_id=item.external_review_id,
                    author=item.author,
                    rating=Decimal(str(item.rating)) if item.rating is not None else None,
                    written_at=item.written_at,
                    text_hash=text_hash,
                    is_processed=False,
                )
                db.add(review)
                try:
                    db.flush()
                    inserted += 1
                    existing_hashes.add((item.source, item.movie_id, text_hash))
                except IntegrityError:
                    # 1-차 dedup: UNIQUE(source, external_review_id) hit
                    db.rollback()
                    continue
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        return inserted

    def _lookup_movie(self, movie_id: str) -> tuple[Optional[str], Optional[int]]:
        db: Session = SessionLocal()
        try:
            movie = db.get(Movie, movie_id)
            if movie is None:
                return None, None
            year = movie.release_year
            if year is None and movie.release_date:
                year = movie.release_date.year
            return movie.movie_title, year
        finally:
            db.close()

    def _load_known_review_ids(self, movie_id: str) -> set[str]:
        """Returns CGV external_review_ids already stored for this movie.

        Used as the early-exit set for full pagination — once we see two
        consecutive API responses entirely composed of these IDs, we know
        we've caught up to the last incremental boundary.
        """
        db: Session = SessionLocal()
        try:
            rows = (
                db.query(Review.external_review_id)
                .filter(
                    Review.movie_id == movie_id,
                    Review.source == SOURCE,
                    Review.external_review_id.isnot(None),
                )
                .all()
            )
            return {r.external_review_id for r in rows if r.external_review_id}
        finally:
            db.close()

    def _load_existing_hashes(self, db: Session, items: list[CollectedReview]) -> set[tuple]:
        movie_ids = {item.movie_id for item in items}
        rows = (
            db.query(Review.source, Review.movie_id, Review.text_hash)
            .filter(Review.movie_id.in_(movie_ids), Review.source == SOURCE)
            .all()
        )
        return {(r.source, r.movie_id, r.text_hash) for r in rows if r.text_hash}


def compute_text_hash(text: str) -> str:
    """SHA-256 of whitespace-normalized text. Case preserved (Korean)."""
    normalized = re.sub(r"\s+", " ", (text or "").strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _build_review_id(source: str, external_id: Optional[str], movie_id: str, text_hash: str) -> str:
    if external_id:
        return f"{source}_{external_id}"[:100]
    # Fallback: hash-based ID when external_id not exposed by CGV
    return f"{source}_{movie_id}_{text_hash[:16]}"[:100]


def _parse_rating(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    match = re.search(r"\d+(?:\.\d+)?", raw)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _parse_written_at(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y.%m.%d",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None
