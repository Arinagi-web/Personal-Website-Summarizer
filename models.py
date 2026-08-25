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