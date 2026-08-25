from __future__ import annotations

import time
from dataclasses import dataclass

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from checkers.javascript import javascript_error_to_bug
from checkers.performance import check_performance
from checkers.accessibility import check_accessibility
from models import BugRecord


@dataclass(slots=True)
class BrowserScanResult:
    """Results produced by browser-based checks for one page."""

    page_url: str
    bugs: list[BugRecord]


class BrowserScanner:
    """
    Owns the Playwright browser lifecycle and runs browser-based
    checkers against pages.
    """

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    def start(self) -> None:
        """Start Playwright and launch Chromium."""
        if self._browser is not None:
            return

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
        )

    def close(self) -> None:
        """Close Chromium and Playwright cleanly."""
        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def scan_page(self, url: str) -> BrowserScanResult:
        """
        Open one URL and run all currently supported browser checkers.
        """

        if self._browser is None:
            raise RuntimeError(
                "BrowserScanner has not been started. "
                "Call start() before scan_page()."
            )

        page = self._browser.new_page()

        javascript_bugs: list[BugRecord] = []

        def handle_page_error(error: object) -> None:
            javascript_bugs.append(
                javascript_error_to_bug(
                    page,
                    error,
                )
            )

        page.on("pageerror", handle_page_error)

        # -----------------------------------------------------
        # Navigation
        # -----------------------------------------------------

        navigation_start = time.perf_counter()

        try:
            page.goto(
                url,
                wait_until="load",
            )
        except Exception:
            pass

        navigation_time = (
            time.perf_counter() - navigation_start
        )

        bugs: list[BugRecord] = []

        # JavaScript errors are captured during navigation.
        bugs.extend(javascript_bugs)

        # -----------------------------------------------------
        # Performance checker
        # -----------------------------------------------------

        performance_start = time.perf_counter()

        load_time_seconds = navigation_time

        performance_bugs = check_performance(
            page,
            load_time_seconds=load_time_seconds,
        )

        performance_time = (
            time.perf_counter() - performance_start
        )

        bugs.extend(performance_bugs)

        # -----------------------------------------------------
        # Accessibility checker
        # -----------------------------------------------------

        accessibility_start = time.perf_counter()

        accessibility_bugs = check_accessibility(
            page
        )

        accessibility_time = (
            time.perf_counter() - accessibility_start
        )

        bugs.extend(accessibility_bugs)

        # -----------------------------------------------------
        # Per-page profile
        # -----------------------------------------------------

        print(
            f"[Browser Profile] {url} | "
            f"navigation={navigation_time:.4f}s | "
            f"javascript={0.0:.4f}s | "
            f"performance={performance_time:.4f}s | "
            f"accessibility={accessibility_time:.4f}s",
            flush=True,
        )

        page.remove_listener(
            "pageerror",
            handle_page_error,
        )

        page.close()

        return BrowserScanResult(
            page_url=url,
            bugs=bugs,
        )

    @staticmethod
    def _javascript_error_to_bug(
        page: Page,
        error: object,
    ) -> list[BugRecord]:
        """
        Convert a Playwright pageerror into a BugRecord.

        This keeps the browser lifecycle in BrowserScanner while
        preserving the same BugRecord structure used by the
        JavaScript checker.
        """

        from checkers.javascript import (
            _extract_location,
        )
        from config import DEFAULT_CONFIG

        message = str(
            getattr(
                error,
                "message",
                error,
            )
        )

        source_file, line_number = _extract_location(
            error,
        )

        return [
            BugRecord(
                page_url=page.url,
                bug_type="JavaScript Error",
                severity=DEFAULT_CONFIG.severity.high,
                description=message,
                evidence=f"JavaScript error: {message}",
                checker="javascript",
                source_file=source_file,
                line_number=line_number,
                error_message=message,
                confidence=1.0,
            )
        ]


def scan_page(
    url: str,
    headless: bool = True,
) -> BrowserScanResult:
    """
    Convenience function for scanning one page.

    Starts and stops the browser automatically.
    """

    scanner = BrowserScanner(
        headless=headless,
    )

    try:
        scanner.start()

        return scanner.scan_page(url)
    finally:
        scanner.close()