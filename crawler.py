from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse
from time import perf_counter

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider

from config import DEFAULT_CONFIG
from utils.logging import configure_logging, get_logger
from utils.urls import is_same_domain, normalize_url


logger = get_logger(__name__)


@dataclass
class CrawlResult:
    """Contains the results produced by a website crawl."""

    seed_url: str
    discovered_urls: list[str] = field(default_factory=list)
    failed_urls: list[str] = field(default_factory=list)
    pages: dict[str, str] = field(default_factory=dict)

    @property
    def pages_discovered(self) -> int:
        """Return the number of successfully discovered pages."""

        return len(self.discovered_urls)


class WebsiteSpider(scrapy.Spider):
    """Scrapy spider responsible for discovering internal HTML pages."""

    name = "website_spider"

    handle_httpstatus_all = True

    def __init__(
        self,
        seed_url: str,
        result: CrawlResult,
        max_pages: int,
        max_depth: int,
        allowed_domain: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.seed_url = normalize_url(seed_url)
        self.result = result
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.allowed_domain = allowed_domain
        # Scrapy's built-in start() implementation will use this.
        self.start_urls = [self.seed_url]

        self._seen_successful_urls: set[str] = set()
        self._request_start_times: dict[str, float] = {}

    def parse(self, response: scrapy.http.Response):
        """Process a response and discover internal links."""

        normalized_url = normalize_url(response.url)

        request_start = self._request_start_times.pop(
            normalized_url,
            None,
        )

        if request_start is not None:
            request_time = perf_counter() - request_start

            print(
                f"[Crawler Request] "
                f"{normalized_url} | "
                f"{request_time:.4f}s",
                flush=True,
            )

        if response.status >= 400:
            logger.warning(
                "HTTP %s | %s",
                response.status,
                normalized_url,
            )

            self.result.failed_urls.append(normalized_url)
            return

        if normalized_url in self._seen_successful_urls:
            return

        # Enforce the application-level page limit before recording
        # another successfully discovered page. Scrapy may already have
        # multiple requests in flight because of concurrency.
        if len(self.result.discovered_urls) >= self.max_pages:
            logger.info(
                "Maximum page limit reached: %d",
                self.max_pages,
            )
            raise CloseSpider(reason="max_pages_reached")

        self._seen_successful_urls.add(normalized_url)
        self.result.discovered_urls.append(normalized_url)
        self.result.pages[normalized_url] = response.text

        logger.info(
            "Discovered page %d/%d | depth=%s | %s",
            len(self.result.discovered_urls),
            self.max_pages,
            response.meta.get("depth", 0),
            normalized_url,
        )

        content_type = response.headers.get(
            b"Content-Type",
            b"",
        ).decode("latin-1").lower()

        if "text/html" not in content_type:
            return

        current_depth = response.meta.get("depth", 0)

        if current_depth >= self.max_depth:
            logger.debug(
                "Maximum crawl depth reached | %s",
                normalized_url,
            )
            return

        for href in response.css("a::attr(href)").getall():
            absolute_url = response.urljoin(href)

            if not self._should_crawl(absolute_url):
                continue

            normalized_link = normalize_url(absolute_url)

            self._request_start_times[normalized_link] = perf_counter()

            yield scrapy.Request(
                url=normalized_link,
                callback=self.parse,
                errback=self.handle_request_error,
                dont_filter=False,
            )

    def _should_crawl(self, url: str) -> bool:
        """Return whether a URL belongs to the configured crawl scope."""

        try:
            normalized_url = normalize_url(url)
        except ValueError:
            return False

        return is_same_domain(
            normalized_url,
            self.allowed_domain,
        )

    def handle_request_error(self, failure):
        """Record and log requests that fail before receiving a response."""

        request_url = failure.request.url

        try:
            normalized_url = normalize_url(request_url)
        except ValueError:
            normalized_url = request_url

        logger.warning(
            "Request failed | %s | %s",
            normalized_url,
            failure.value,
        )

        self.result.failed_urls.append(normalized_url)
     


def crawl(
    seed_url: str,
    max_pages: int | None = None,
    max_depth: int | None = None,
) -> CrawlResult:
    """
    Run an isolated Scrapy crawl and return the discovered pages.

    Scrapy runs in a separate Python process so that its Twisted
    reactor lifecycle cannot interfere with the main application.
    """

    import json
    import subprocess
    import sys

    configure_logging()

    seed_url = normalize_url(seed_url)

    crawl_config = DEFAULT_CONFIG.crawl

    effective_max_pages = (
        max_pages
        if max_pages is not None
        else crawl_config.max_pages
    )

    effective_max_depth = (
        max_depth
        if max_depth is not None
        else crawl_config.max_depth
    )

    if effective_max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    if effective_max_depth < 0:
        raise ValueError("max_depth cannot be negative")

    logger.info(
        "Starting isolated crawl | seed=%s | max_pages=%d | max_depth=%d",
        seed_url,
        effective_max_pages,
        effective_max_depth,
    )

    command = [
        sys.executable,
        "crawler_worker.py",
        seed_url,
        str(effective_max_pages),
        str(effective_max_depth),
    ]

    subprocess_start = perf_counter()

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    subprocess_time = (
        perf_counter() - subprocess_start
    )
    if completed.stderr.strip():
        print(
            completed.stderr,
            end="",
            flush=True,
        )
    print(
        f"[Crawler Parent Profile] "
        f"subprocess={subprocess_time:.4f}s",
        flush=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "Crawler process failed.\n"
            f"Exit code: {completed.returncode}\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )

    output_lines = [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip()
    ]

    if not output_lines:
        raise RuntimeError(
            "Crawler process returned no result."
        )

    try:
        data = json.loads(output_lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Crawler process returned invalid JSON.\n"
            f"Output:\n{completed.stdout}"
        ) from exc

    result = CrawlResult(
        seed_url=data["seed_url"],
        discovered_urls=data["discovered_urls"],
        failed_urls=data["failed_urls"],
        pages=data["pages"]
    )

    logger.info(
        "Crawl finished | discovered=%d | failed=%d",
        len(result.discovered_urls),
        len(result.failed_urls),
    )

    return result