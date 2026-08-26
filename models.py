"""Data models used by Website Summarizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class BugRecord:
    """Represents a single finding produced by any checker."""

    page_url: str
    bug_type: str
    severity: str
    description: str
    element: Optional[str] = None
    evidence: Optional[str] = None
    checker: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    target_url: Optional[str] = None
    http_status: Optional[int] = None
    selector: Optional[str] = None
    error_message: Optional[str] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    confidence: Optional[float] = None
    screenshot_path: Optional[str] = None


@dataclass(slots=True)
class PageContent:
    """Represents extracted and ranked content from one webpage."""

    url: str
    raw_html: str
    extracted_text: str
    char_count: int = field(init=False)
    extraction_method: str = "failed"

    def __post_init__(self) -> None:
        """Calculate the character count from extracted text."""
        self.char_count = len(self.extracted_text)

    @property
    def is_empty(self) -> bool:
        """Return True when the extracted content is too short."""
        return self.char_count < 100


@dataclass(slots=True)
class SummaryResult:
    """Represents the AI-generated summary for one webpage."""

    url: str
    summary: str = ""
    key_points: list[str] = field(
        default_factory=list
    )
    model_used: str = ""
    input_chars: int = 0
    was_chunked: bool = False
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Return True when a non-empty summary was generated."""
        return self.error is None and bool(self.summary)


@dataclass(slots=True)
class PageMetadata:
    """Represents metadata extracted from one webpage."""

    url: str
    title: str = ""
    meta_description: str = ""
    h1: str = ""
    word_count: int = 0
    language: str = ""
    extraction_method: str = ""