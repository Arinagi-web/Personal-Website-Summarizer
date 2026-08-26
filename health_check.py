import asyncio
import sys

# pyrefly: ignore [missing-import]
from playwright.async_api import async_playwright


async def main() -> None:
    print(f"Python: {sys.version}")
    print("Starting Playwright...")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()
        await page.goto("https://example.com", wait_until="domcontentloaded")

        print(f"Page title: {await page.title()}")
        print(f"Page URL: {page.url}")

        await browser.close()

    print("Playwright + Chromium: OK")


if __name__ == "__main__":
    asyncio.run(main())