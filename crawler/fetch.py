"""HTTP fetcher: throttled, retried, ETag-aware."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from crawler.config import (
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)


@dataclass
class FetchResult:
    url: str
    status: int
    text: str
    etag: Optional[str]
    last_modified: Optional[str]
    from_cache: bool = False


class Fetcher:
    """Single-threaded fetcher with sleep-based throttling and retry."""

    def __init__(self, delay_seconds: float = REQUEST_DELAY_SECONDS):
        self._client = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        self._delay = delay_seconds
        self._last_request_at = 0.0

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPError,)),
        reraise=True,
    )
    def _do_get(self, url: str, headers: dict[str, str]) -> httpx.Response:
        return self._client.get(url, headers=headers)

    def get(
        self,
        url: str,
        prev_etag: Optional[str] = None,
        prev_last_modified: Optional[str] = None,
        min_delay: Optional[float] = None,
    ) -> FetchResult:
        # Throttle — honour the larger of the configured delay and any
        # per-request minimum (e.g. a stricter robots.txt Crawl-delay for a
        # given doc source).
        delay = self._delay if min_delay is None else max(self._delay, min_delay)
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < delay:
            time.sleep(delay - elapsed)
        headers: dict[str, str] = {}
        if prev_etag:
            headers["If-None-Match"] = prev_etag
        if prev_last_modified:
            headers["If-Modified-Since"] = prev_last_modified
        r = self._do_get(url, headers)
        self._last_request_at = time.monotonic()
        if r.status_code == 304:
            return FetchResult(
                url=url,
                status=304,
                text="",
                etag=prev_etag,
                last_modified=prev_last_modified,
                from_cache=True,
            )
        if r.status_code >= 400 and r.status_code != 404:
            r.raise_for_status()
        return FetchResult(
            url=url,
            status=r.status_code,
            text=r.text,
            etag=r.headers.get("ETag"),
            last_modified=r.headers.get("Last-Modified"),
        )
