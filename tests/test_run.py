from __future__ import annotations

from Summarizer.run import run
from models import SummaryResult, PageMetadata


def test_run_pipeline_returns_tuple(monkeypatch):
    """run() should process a single HTML string and return a tuple."""

    html = """
        <html>
            <head>
                <title>Example Website</title>
            </head>
            <body>
                <main>
                    <h1>Welcome to Example</h1>
                    <p>
                        This is the main content of the example website.
                    </p>
                </main>
            </body>
        </html>
    """

    expected_summary = SummaryResult(url="https://example.com/", summary="Test summary")
    expected_metadata = PageMetadata(url="https://example.com/")

    def fake_summarize(*args, **kwargs):
        return expected_summary

    monkeypatch.setattr(
        "Summarizer.run.summarize_page",
        fake_summarize,
    )

    summary, metadata = run("https://example.com/", html)

    assert summary is expected_summary
    assert metadata.title == "Example Website"


def test_run_handles_exception(monkeypatch):
    """run() should return a failure result when an exception occurs."""

    def fake_extract(*args, **kwargs):
        raise ValueError("Extraction failed")

    monkeypatch.setattr(
        "Summarizer.run.extract_page_contents",
        fake_extract,
    )

    summary, metadata = run("https://example.com/", "<html></html>")

    assert not summary.success
    assert summary.error == "Extraction failed"