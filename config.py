from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True, slots=True)
class ConcurrencyConfig:
    """Controls resource usage during a scan."""

    max_concurrent_pages: int = 1
    max_concurrent_http_requests: int = 5


@dataclass(frozen=True, slots=True)
class CrawlConfig:
    """Controls crawler scope and request behaviour."""

    max_pages: int = 100
    max_depth: int = 5
    request_timeout_seconds: float = 15.0
    request_delay_seconds: float = 0.1
    respect_robots_txt: bool = True
    performance_threshold_seconds: float = 2.0


@dataclass(frozen=True, slots=True)
class SeverityConfig:
    """Centralized severity configuration."""

    critical: Final[str] = "Critical"
    high: Final[str] = "High"
    medium: Final[str] = "Medium"
    low: Final[str] = "Low"


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Application-wide configuration."""

    concurrency: ConcurrencyConfig = field(
        default_factory=ConcurrencyConfig
    )
    crawl: CrawlConfig = field(
        default_factory=CrawlConfig
    )
    severity: SeverityConfig = field(
        default_factory=SeverityConfig
    )


DEFAULT_CONFIG = AppConfig()