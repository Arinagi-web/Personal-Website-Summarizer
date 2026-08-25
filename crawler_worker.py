from __future__ import annotations

import json
import sys

from time import perf_counter
from scrapy.crawler import CrawlerProcess

from crawler import CrawlResult, WebsiteSpider
from config import DEFAULT_CONFIG
from utils.logging import configure_logging


def run_worker(
    seed_url: str,
    max_pages: int,
    max_depth: int,
) -> None:
    """Run one isolated Scrapy crawl and emit its result as JSON."""

    worker_start = perf_counter()

    configure_logging()

    result = CrawlResult(seed_url=seed_url)

    from urllib.parse import urlparse

    parsed_seed = urlparse(seed_url)

    if not parsed_seed.hostname:
        raise ValueError(
            f"Unable to determine hostname from URL: {seed_url}"
        )

    crawl_config = DEFAULT_CONFIG.crawl
    concurrency_config = DEFAULT_CONFIG.concurrency

    settings = {
        "ROBOTSTXT_OBEY": crawl_config.respect_robots_txt,
        "CONCURRENT_REQUESTS": (
            concurrency_config.max_concurrent_http_requests
        ),
        "DOWNLOAD_DELAY": crawl_config.request_delay_seconds,
        "DOWNLOAD_TIMEOUT": crawl_config.request_timeout_seconds,
        "DEPTH_LIMIT": max_depth,
        "CLOSESPIDER_PAGECOUNT": max_pages,
        "LOG_ENABLED": False,
        "USER_AGENT": "AutoBugTestCrawler/0.1",
    }

    process_start = perf_counter()

    process = CrawlerProcess(
        settings=settings,
    )

    process.crawl(
        WebsiteSpider,
        seed_url=seed_url,
        result=result,
        max_pages=max_pages,
        max_depth=max_depth,
        allowed_domain=parsed_seed.hostname.lower(),
    )

    process_create_time = (
        perf_counter() - process_start
    )

    crawl_start = perf_counter()

    process.start()

    crawl_time = (
        perf_counter() - crawl_start
    )

    serialization_start = perf_counter()

    output = {
        "seed_url": result.seed_url,
        "discovered_urls": result.discovered_urls,
        "failed_urls": result.failed_urls,
        "pages": result.pages,
    }

    json_output = json.dumps(
        output,
        ensure_ascii=False,
    )

    serialization_time = (
        perf_counter() - serialization_start
    )

    total_worker_time = (
        perf_counter() - worker_start
    )

    print(
        f"[Crawler Profile] ",
        f"process_setup={process_create_time:.4f}s | ",
        f"crawl={crawl_time:.4f}s | ",
        f"serialization={serialization_time:.4f}s | ",
        f"total_worker={total_worker_time:.4f}s | ",
        file=sys.stderr,
        flush=True,
    )

    print(json_output)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: python crawler_worker.py "
            "<seed_url> <max_pages> <max_depth>"
        )

    run_worker(
        seed_url=sys.argv[1],
        max_pages=int(sys.argv[2]),
        max_depth=int(sys.argv[3]),
    )