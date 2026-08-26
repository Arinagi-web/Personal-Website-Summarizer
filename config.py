"""Application configuration for Website Summarizer."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv


load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required application configuration is invalid."""


@dataclass(slots=True)
class CrawlConfig:
    """Configuration controlling website crawling."""

    max_pages: int = 1
    max_depth: int = 0
    request_timeout_seconds: float = 15.0
    request_delay_seconds: float = 0.1
    respect_robots_txt: bool = True

@dataclass(slots=True)
class ConcurrencyConfig:
    """Configuration controlling concurrent work."""

    max_concurrent_http_requests: int = 8
    max_concurrent_pages: int = 4

@dataclass(slots=True)
class ExtractionConfig:
    """Configuration controlling HTML extraction and ranking."""

    min_content_length: int = 100
    max_content_chars: int = 24000
    max_sections_to_rank: int = 20


@dataclass(slots=True)
class AIConfig:
    """Configuration controlling the AI summarization provider."""

    provider: str = os.getenv("AI_PROVIDER", "groq")
    model: str = os.getenv(
        "AI_MODEL",
        "llama-3.1-8b-instant",
    )
    api_key: str = os.getenv("GROQ_API_KEY", "")
    base_url: str = (
        "https://api.groq.com/openai/v1/chat/completions"
    )
    max_output_tokens: int = 1500
    chunk_size_chars: int = 24000
    temperature: float = 0.3
    request_timeout: float = 30.0


@dataclass(slots=True)
class AppConfig:
    """Top-level configuration for the summarizer application."""

    crawl: CrawlConfig = field(
        default_factory=CrawlConfig,
    )
    concurrency: ConcurrencyConfig = field(
        default_factory=ConcurrencyConfig,
    )
    extraction: ExtractionConfig = field(
        default_factory=ExtractionConfig,
    )
    ai: AIConfig = field(
        default_factory=AIConfig,
    )


DEFAULT_CONFIG = AppConfig()


def validate_config(
    config: AppConfig = DEFAULT_CONFIG,
) -> None:
    """Validate configuration required before application startup."""
    if not config.ai.api_key.strip():
        raise ConfigurationError(
            "GROQ_API_KEY is missing. "
            "Add your Groq API key to the .env file "
            "before running Website Summarizer."
        )

    if config.ai.provider == "groq" and not config.ai.base_url:
        raise ConfigurationError(
            "Groq provider is configured without an API base URL."
        )

    if config.crawl.max_pages < 1:
        raise ConfigurationError(
            "crawl.max_pages must be at least 1."
        )

    if config.crawl.max_depth < 0:
        raise ConfigurationError(
            "crawl.max_depth cannot be negative."
        )

    if config.extraction.min_content_length < 0:
        raise ConfigurationError(
            "extraction.min_content_length cannot be negative."
        )

    if config.extraction.max_content_chars < 1:
        raise ConfigurationError(
            "extraction.max_content_chars must be greater than 0."
        )

    if config.extraction.max_sections_to_rank < 1:
        raise ConfigurationError(
            "extraction.max_sections_to_rank must be at least 1."
        )

    if config.ai.max_output_tokens < 1:
        raise ConfigurationError(
            "ai.max_output_tokens must be greater than 0."
        )

    if config.ai.chunk_size_chars < 1:
        raise ConfigurationError(
            "ai.chunk_size_chars must be greater than 0."
        )

    if not 0.0 <= config.ai.temperature <= 2.0:
        raise ConfigurationError(
            "ai.temperature must be between 0.0 and 2.0."
        )


def get_provider_name(
    config: AppConfig = DEFAULT_CONFIG,
) -> Literal["groq", "other"]:
    """Return the configured provider category."""
    if config.ai.provider.lower() == "groq":
        return "groq"

    return "other"