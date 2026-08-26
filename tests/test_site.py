from __future__ import annotations

from Summarizer.site import summarize_site
from models import SummaryResult, PageMetadata


def test_single_page_returns_one_result(monkeypatch):
    class FakeCrawlResult:
        pages = {"https://example.com/": "<html></html>"}
        failed_urls = []

    monkeypatch.setattr(
        "Summarizer.site.crawl",
        lambda *args, **kwargs: FakeCrawlResult(),
    )

    expected_summary = SummaryResult(url="https://example.com/", summary="Test")
    expected_meta = PageMetadata(url="https://example.com/")

    def fake_run(*args, **kwargs):
        return expected_summary, expected_meta

    monkeypatch.setattr("Summarizer.site.run", fake_run)

    results = summarize_site("https://example.com/")

    assert len(results) == 1
    assert results[0][0] is expected_summary
    assert results[0][1] is expected_meta


def test_failed_crawl_returns_empty_list_with_logged_error(monkeypatch):
    class FakeCrawlResult:
        pages = {}
        failed_urls = ["https://example.com/"]

    monkeypatch.setattr(
        "Summarizer.site.crawl",
        lambda *args, **kwargs: FakeCrawlResult(),
    )

    results = summarize_site("https://example.com/")
    assert len(results) == 0


def test_summarize_site_handles_page_exception(monkeypatch):
    class FakeCrawlResult:
        pages = {"https://example.com/": "<html></html>"}
        failed_urls = []

    monkeypatch.setattr(
        "Summarizer.site.crawl",
        lambda *args, **kwargs: FakeCrawlResult(),
    )

    def fake_run(*args, **kwargs):
        raise ValueError("Error running page")

    monkeypatch.setattr("Summarizer.site.run", fake_run)

    results = summarize_site("https://example.com/")

    assert len(results) == 1
    summary, metadata = results[0]
    assert not summary.success
    assert summary.error == "Error running page"