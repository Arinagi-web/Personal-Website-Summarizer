from __future__ import annotations

# pyrefly: ignore [missing-import]
import pytest

from config import (
    AIConfig,
    AppConfig,
    ConfigurationError,
    DEFAULT_CONFIG,
    validate_config,
)
from models import PageContent, SummaryResult


def test_page_content_is_empty_when_short() -> None:
    """PageContent should be empty below 100 characters."""
    content = PageContent(
        url="https://example.com",
        raw_html="<html></html>",
        extracted_text="x" * 99,
        extraction_method="beautifulsoup",
    )

    assert content.char_count == 99
    assert content.is_empty is True


def test_page_content_is_not_empty_at_100_chars() -> None:
    """PageContent should not be empty at exactly 100 characters."""
    content = PageContent(
        url="https://example.com",
        raw_html="<html></html>",
        extracted_text="x" * 100,
        extraction_method="beautifulsoup",
    )

    assert content.char_count == 100
    assert content.is_empty is False


def test_page_content_char_count_is_automatic() -> None:
    """PageContent should calculate its character count."""
    text = "This is extracted webpage content."

    content = PageContent(
        url="https://example.com",
        raw_html="<html></html>",
        extracted_text=text,
        extraction_method="trafilatura",
    )

    assert content.char_count == len(text)


def test_summary_result_success_when_summary_exists() -> None:
    """SummaryResult should report success for a valid summary."""
    result = SummaryResult(
        url="https://example.com",
        summary="This page explains an important topic.",
    )

    assert result.success is True


def test_summary_result_success_false_when_error_exists() -> None:
    """SummaryResult should fail when an error is present."""
    result = SummaryResult(
        url="https://example.com",
        summary="This page has a summary.",
        error="API request failed.",
    )

    assert result.success is False


def test_summary_result_success_false_when_summary_empty() -> None:
    """SummaryResult should fail when no summary was generated."""
    result = SummaryResult(
        url="https://example.com",
    )

    assert result.success is False


def test_default_config_loads_without_error() -> None:
    """DEFAULT_CONFIG should be constructible without credentials."""
    assert isinstance(DEFAULT_CONFIG, AppConfig)
    assert DEFAULT_CONFIG.crawl.max_pages == 1
    assert DEFAULT_CONFIG.crawl.max_depth == 0
    assert DEFAULT_CONFIG.ai.provider == "groq"
    assert DEFAULT_CONFIG.ai.model == "llama-3.1-8b-instant"


def test_default_extraction_config_values() -> None:
    """Extraction defaults should match the project specification."""
    assert DEFAULT_CONFIG.extraction.min_content_length == 100
    assert DEFAULT_CONFIG.extraction.max_content_chars == 24000
    assert DEFAULT_CONFIG.extraction.max_sections_to_rank == 20


def test_default_ai_config_values() -> None:
    """AI defaults should match the project specification."""
    assert DEFAULT_CONFIG.ai.max_output_tokens == 1500
    assert DEFAULT_CONFIG.ai.chunk_size_chars == 24000
    assert DEFAULT_CONFIG.ai.temperature == 0.3
    assert DEFAULT_CONFIG.ai.request_timeout == 30.0


def test_configuration_error_when_api_key_is_empty() -> None:
    """Validation should reject a missing Groq API key."""
    config = AppConfig(
        ai=AIConfig(api_key=""),
    )

    with pytest.raises(
        ConfigurationError,
        match="GROQ_API_KEY is missing",
    ):
        validate_config(config)


def test_configuration_error_when_api_key_is_whitespace() -> None:
    """Validation should reject whitespace-only API keys."""
    config = AppConfig(
        ai=AIConfig(api_key="   "),
    )

    with pytest.raises(
        ConfigurationError,
        match="GROQ_API_KEY is missing",
    ):
        validate_config(config)