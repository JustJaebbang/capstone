"""KOBIS movie -> CGV movie code resolver (Playwright-backed).

CGV's search endpoints are protected by the same HMAC signing + Cloudflare
bot management that the review API uses. Bare `requests` returns 403/401.
We drive a real Chromium via Playwright so CGV's own JS handles signing,
then read movieChart codes from the rendered search results.

Result is meant to be cached in `movies.cgv_movie_code` — this resolver
is the slow path; the hot path is a single DB read.

Step-7+ verification target: the search URL pattern and result-link selector
are best-effort. If a known popular movie returns no candidates, check the
logged page HTML / take a debug screenshot to adjust.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

CGV_SEARCH_URL_TEMPLATE = "https://cgv.co.kr/tme/itgrSrch?swrd={query}"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_NAV_TIMEOUT_MS = 30000
DEFAULT_POST_LOAD_WAIT_MS = 3000

# Same stealth tweaks as CGVReviewClient — Cloudflare bot detection hides the
# obvious automation markers.
_STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
window.chrome = window.chrome || { runtime: {} };
"""


@dataclass
class CGVMovieHit:
    code: str
    title: str


class CGVMovieResolver:
    """Resolves (title, release_year) → CGV internal movie code (midx / movNo)."""

    def __init__(self, headless: bool = True,
                 nav_timeout_ms: int = DEFAULT_NAV_TIMEOUT_MS,
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

    def __enter__(self) -> "CGVMovieResolver":
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

    def resolve(self, title: str, release_year: Optional[int] = None) -> Optional[str]:
        """Returns the CGV movie code for the given title, or None if not found.

        Strategy:
          1. Try the original title as search query.
          2. If no exact match, try query variants (CGV uses hyphens where
             KOBIS uses colons; punctuation-stripped form; first chunk).
          3. For each query, only accept exact normalized title match
             against the *original* target — no fallback to first result
             (CGV's empty-search default would mismap every miss).
        """
        if not title:
            return None
        self._ensure_started()
        normalized_target = _normalize(title)

        for variant in self._query_variants(title):
            hits = self._search_for(variant)
            if not hits:
                continue
            exact = [h for h in hits if _normalize(h.title) == normalized_target]
            if exact:
                logger.info(
                    "resolved %r -> %s (via query %r)", title, exact[0].code, variant,
                )
                return exact[0].code
            logger.info(
                "variant %r returned %d hit(s) but no exact match: %s",
                variant, len(hits), [h.title for h in hits[:3]],
            )

        logger.warning("no exact match for %r across all query variants", title)
        return None

    def _search_for(self, query: str) -> list[CGVMovieHit]:
        """Single search request — open a page, navigate, parse, close."""
        page = self._context.new_page()
        page.set_default_timeout(self.nav_timeout_ms)
        try:
            url = CGV_SEARCH_URL_TEMPLATE.format(query=quote(query))
            page.goto(url, wait_until="domcontentloaded", timeout=self.nav_timeout_ms)
            for _ in range(3):
                page.evaluate("window.scrollBy(0, document.body.scrollHeight / 3)")
                page.wait_for_timeout(400)
            page.wait_for_timeout(self.post_load_wait_ms)
            return self._parse_hits(page)
        finally:
            page.close()

    @staticmethod
    def _query_variants(title: str) -> list[str]:
        """Build query variants in order of likely success.

        Original first — most movies resolve in one shot. Variants try
        common CGV/KOBIS title-format mismatches:
        - Colon → hyphen (CGV's preferred separator for subtitles)
        - All punctuation stripped to spaces
        - First chunk before colon/comma (broad search; exact-match filter
          still applies, so safe)
        Duplicates are de-duped while preserving order.
        """
        variants: list[str] = []
        def _add(v: str) -> None:
            v = v.strip()
            if v and v not in variants:
                variants.append(v)

        _add(title)
        if ":" in title:
            _add(title.replace(": ", "-").replace(":", "-"))
            _add(title.replace(":", " "))
        clean = re.sub(r"[:\-_,.·!?\"'\(\)\[\]]+", " ", title)
        clean = re.sub(r"\s+", " ", clean)
        _add(clean)
        head = re.split(r"[:,\-]", title, 1)[0]
        _add(head)
        return variants

    def _parse_hits(self, page) -> list[CGVMovieHit]:
        """Extract (code, title) pairs from the search results DOM.

        CGV's search results are Next.js cards where the actual click handler
        is JS-driven — the movie code does NOT appear in any href. The code
        IS embedded in the poster image URL path:

            src="https://cdn.cgv.co.kr/cgvpomsfilm/Movie/Thumbnail/Poster/
                 030001/30001046/30001046_592.jpg"
            alt="군체 포스터"

        So we anchor on `<img>` elements whose alt contains "포스터" and src
        matches the cgvpomsfilm poster URL — that combination filters out
        event banners and other non-movie imagery.
        """
        POSTER_RE = re.compile(r"cgvpomsfilm/Movie/Thumbnail/Poster/\d+/(\d+)/")
        images = page.locator("img[alt*='포스터'][src*='cgvpomsfilm']").all()
        hits: list[CGVMovieHit] = []
        seen: set[str] = set()
        for img in images:
            try:
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                m = POSTER_RE.search(src)
                if not m:
                    continue
                code = m.group(1)
                if code in seen:
                    continue
                seen.add(code)
                title = re.sub(r"\s*포스터\s*$", "", alt).strip()
                hits.append(CGVMovieHit(code=code, title=title))
            except Exception:
                continue
        return hits

    def _dump_debug(self, page, title: str) -> None:
        if not self.debug_dump_dir:
            return
        try:
            from pathlib import Path
            d = Path(self.debug_dump_dir)
            d.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^A-Za-z0-9_\-가-힣]+", "_", title)[:40]
            page.screenshot(path=str(d / f"resolve_{safe}.png"), full_page=True)
            (d / f"resolve_{safe}.html").write_text(page.content(), encoding="utf-8")
            logger.info("debug dump saved to %s", d)
        except Exception as exc:
            logger.warning("debug dump failed: %s", exc)


_PUNCT_RE = re.compile(r"[\s:\-_,.·　·!?\"'\(\)\[\]]+")


def _normalize(text: str) -> str:
    """Lowercase + strip whitespace and common Korean/English punctuation.

    Tolerates variants like '듄: 파트 2' ↔ '듄 파트2' ↔ '듄-파트2'.
    """
    return _PUNCT_RE.sub("", (text or "")).lower()
