from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import requests

logger = logging.getLogger(__name__)


KOBIS_BASE = "https://www.kobis.or.kr/kobisopenapi/webservice/rest"
KOBIS_DAILY_BOXOFFICE_URL = f"{KOBIS_BASE}/boxoffice/searchDailyBoxOfficeList.json"
KOBIS_MOVIE_INFO_URL = f"{KOBIS_BASE}/movie/searchMovieInfo.json"

DEFAULT_TIMEOUT = 10  # seconds


class KOBISClient:
    """KOBIS Open API thin client.

    Stateless HTTP + JSON parsing only. No DB. No schema enrichment beyond
    what KOBIS itself returns. Caller composes higher-level flows.
    """

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT):
        if not api_key:
            raise ValueError("KOBIS API key is required")
        self.api_key = api_key
        self.timeout = timeout

    def _request_json(self, url: str, params: dict[str, Any], endpoint_label: str) -> dict[str, Any]:
        """GET + JSON parse with API-key-safe error reporting.

        `requests` puts the full URL (including ?key=...) into its exception
        message. We catch any request error and re-raise with a sanitized
        message that omits the key, so logs / tracebacks never expose it.
        """
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            safe_params = {k: ("***REDACTED***" if k == "key" else v) for k, v in params.items()}
            raise RuntimeError(
                f"KOBIS request failed [{endpoint_label}] params={safe_params} error_type={type(exc).__name__}"
            ) from None  # `from None` suppresses original chain so URL never surfaces

        payload = resp.json()
        if "faultInfo" in payload:
            fault = payload["faultInfo"]
            raise RuntimeError(f"KOBIS API fault [{endpoint_label}]: {fault}")
        return payload

    def fetch_daily_boxoffice(self, target_date: date | None = None) -> list[dict[str, Any]]:
        """KOBIS daily boxoffice top 10.

        target_date defaults to yesterday (KOBIS only publishes prior-day data).
        Returns the raw `dailyBoxOfficeList` entries.
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)

        params = {"key": self.api_key, "targetDt": target_date.strftime("%Y%m%d")}
        payload = self._request_json(KOBIS_DAILY_BOXOFFICE_URL, params, "daily_boxoffice")
        return payload.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

    def fetch_movie_info(self, movie_cd: str) -> dict[str, Any]:
        """KOBIS movie detail by movieCd. Returns the `movieInfo` sub-object."""
        params = {"key": self.api_key, "movieCd": movie_cd}
        payload = self._request_json(KOBIS_MOVIE_INFO_URL, params, f"movie_info[{movie_cd}]")
        return payload.get("movieInfoResult", {}).get("movieInfo", {})
