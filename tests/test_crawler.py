from crawler import crawl
from pathlib import Path


LOCAL_SITE = "http://127.0.0.1:8000/"


def test_crawler_respects_robots_txt() -> None:
    robots_path = Path("test_site") / "robots.txt"

    robots_path.write_text(
        "User-agent: *\n"
        "Disallow: /grammar.html\n",
        encoding="utf-8",
    )

    try:
        result = crawl(
            LOCAL_SITE,
            max_pages=20,
            max_depth=5,
        )

        assert "http://127.0.0.1:8000/grammar.html" not in (
            result.discovered_urls
        )

        assert "http://127.0.0.1:8000/about.html" in (
            result.discovered_urls
        )

    finally:
        if robots_path.exists():
            robots_path.unlink()


def test_crawler_stays_on_target_domain() -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=20,
        max_depth=5,
    )

    for url in result.discovered_urls:
        assert url.startswith("http://127.0.0.1:8000/")


def test_crawler_deduplicates_urls() -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=20,
        max_depth=5,
    )

    assert len(result.discovered_urls) == len(
        set(result.discovered_urls)
    )


def test_crawler_respects_max_pages() -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=3,
        max_depth=5,
    )

    assert len(result.discovered_urls) <= 3


def test_crawler_respects_max_depth(
    require_local_server,
) -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=20,
        max_depth=0,
    )

    assert result.pages_discovered == 1

def test_crawler_respects_robots_txt(
    require_local_server,
) -> None:
    robots_path = Path("test_site") / "robots.txt"

    robots_path.write_text(
        "User-agent: *\n"
        "Disallow: /grammar.html\n",
        encoding="utf-8",
    )

    try:
        result = crawl(
            LOCAL_SITE,
            max_pages=20,
            max_depth=5,
        )

        assert "http://127.0.0.1:8000/grammar.html" not in (
            result.discovered_urls
        )

        assert "http://127.0.0.1:8000/about.html" in (
            result.discovered_urls
        )

    finally:
        if robots_path.exists():
            robots_path.unlink()

def test_crawler_discovers_local_pages(
    require_local_server,
) -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=20,
        max_depth=5,
    )

    assert result.pages_discovered > 1
    assert LOCAL_SITE in result.discovered_urls
    assert "http://127.0.0.1:8000/about.html" in result.discovered_urls

def test_crawler_retains_page_html(
    require_local_server,
) -> None:
    result = crawl(
        LOCAL_SITE,
        max_pages=20,
        max_depth=5,
    )

    assert LOCAL_SITE in result.pages
    assert "<html" in result.pages[LOCAL_SITE].lower()