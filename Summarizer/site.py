from __future__ import annotations

from crawler import crawl
from models import SummaryResult, PageMetadata
from Summarizer.run import run
from utils.logging import get_logger
from tqdm import tqdm

logger = get_logger(__name__)

def summarize_site(
    site_url: str,
    max_pages: int | None = None,
    max_depth: int | None = None,
) -> list[tuple[SummaryResult, PageMetadata]]:
    """Run the summarization pipeline for all crawled pages."""

    crawl_result = crawl(
        site_url,
        max_pages=max_pages,
        max_depth=max_depth,
    )

    results: list[tuple[SummaryResult, PageMetadata]] = []
    
    for page_url, html in tqdm(crawl_result.pages.items(), desc="Summarizing pages"):
        try:
            summary, analysis = run(page_url, html)
            results.append((summary, analysis))
        except Exception as exc:
            logger.error(f"Site summarizer failed for {page_url}: {exc}")
            results.append((
                SummaryResult(url=page_url, error=str(exc)),
                PageMetadata(url=page_url)
            ))

    return results