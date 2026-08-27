from __future__ import annotations
from playwright.sync_api import sync_playwright
from utils.logging import get_logger

logger = get_logger(__name__)

class JavaScriptFetcher:
    """A Playwright-based fetcher for JS-rendered and bot-protected pages."""
    
    def __init__(self, headless: bool = True):
        """Initialize the fetcher with the specified headless setting.
        
        Does not launch the browser immediately.
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self) -> None:
        """Launch the Playwright browser and setup the context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True
        )

    def fetch(self, url: str) -> str:
        """Fetch the page content using the initialized browser context."""
        if not self.context:
            logger.error("Browser context not started.")
            return ""
            
        page = self.context.new_page()
        try:
            try:
                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=15000,
                )
            except Exception:
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
            page.wait_for_timeout(2000)
            return page.content()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""
        finally:
            try:
                page.close()
            except Exception:
                pass

    def close(self) -> None:
        """Close the browser context, browser, and playwright instance."""
        if self.context:
            try:
                self.context.close()
            except Exception as e:
                logger.error(f"Error closing context: {e}")
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                logger.error(f"Error stopping playwright: {e}")

    def __enter__(self) -> JavaScriptFetcher:
        """Context manager entry point."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit point."""
        self.close()

def fetch_with_browser(url: str) -> str:
    """Fetch a JS-rendered page using Playwright.
    
    Returns raw HTML string or empty string on failure.
    """
    with JavaScriptFetcher() as fetcher:
        return fetcher.fetch(url)