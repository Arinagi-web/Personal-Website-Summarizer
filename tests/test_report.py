from models import SummaryResult, PageMetadata
from Summarizer.report import format_report


def test_success_report_contains_summary_text():
    summary = SummaryResult(
        url="https://example.com",
        summary="This is a test summary.",
        key_points=["Point 1", "Point 2"],
    )
    metadata = PageMetadata(
        url="https://example.com",
    )
    report = format_report(summary, metadata, "https://example.com")
    
    assert "This is a test summary." in report


def test_success_report_contains_all_key_points():
    summary = SummaryResult(
        url="https://example.com",
        summary="This is a test summary.",
        key_points=["Point 1", "Point 2"],
    )
    metadata = PageMetadata(
        url="https://example.com",
    )
    report = format_report(summary, metadata, "https://example.com")
    
    assert "• Point 1" in report
    assert "• Point 2" in report


def test_success_report_contains_url():
    summary = SummaryResult(
        url="https://example.com",
        summary="This is a test summary.",
    )
    metadata = PageMetadata(
        url="https://example.com",
    )
    report = format_report(summary, metadata, "https://example.com")
    
    assert "URL   : https://example.com" in report


def test_failure_report_contains_error_message():
    summary = SummaryResult(
        url="https://example.com",
        error="This is an error message.",
    )
    report = format_report(summary, None, "https://example.com")
    
    assert "Error : This is an error message." in report
    assert "SUMMARY FAILED" in report


def test_failure_report_does_not_contain_key_points_section():
    summary = SummaryResult(
        url="https://example.com",
        error="This is an error message.",
    )
    report = format_report(summary, None, "https://example.com")
    
    assert "KEY POINTS" not in report