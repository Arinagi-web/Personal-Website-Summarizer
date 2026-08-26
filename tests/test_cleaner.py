from Summarizer.cleaner import clean_page_content
from Summarizer.extractor import extract_page_contents


HTML = """
<html>
    <head>
        <title>Example Website</title>
    </head>

    <body>

        <header>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>

        <main>
            <h1>Welcome to Example</h1>

            <p>
                This is the main content of the website.
            </p>

            <p>
                This is additional information for visitors.
            </p>

            <p>
                This is additional information for visitors.
            </p>
        </main>

        <footer>
            Copyright 2026 Example
        </footer>

    </body>
</html>
"""


def test_clean_page_content_preserves_meaningful_content():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert cleaned.url == "https://example.com/"
    assert cleaned.title == "Example Website"

    assert "Welcome to Example" in cleaned.headings

    assert (
        "This is the main content of the website."
        in cleaned.paragraphs
    )

    assert (
        "This is additional information for visitors."
        in cleaned.paragraphs
    )


def test_clean_page_content_removes_duplicate_text():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert cleaned.paragraphs.count(
        "This is additional information for visitors."
    ) == 1


def test_clean_page_content_does_not_include_navigation():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert "Home" not in cleaned.text
    assert "About" not in cleaned.text
    assert "Contact" not in cleaned.text


def test_clean_page_content_calculates_statistics():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert cleaned.word_count > 0
    assert cleaned.character_count > 0
    assert cleaned.character_count == len(cleaned.text)


def test_cleaner_reports_content_reduction():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert cleaned.original_word_count > 0
    assert cleaned.original_character_count > 0

    assert cleaned.words_removed >= 0
    assert cleaned.characters_removed >= 0

    assert 0 <= cleaned.word_reduction_percent <= 100
    assert 0 <= cleaned.character_reduction_percent <= 100


def test_cleaner_reduction_matches_counts():
    page = extract_page_contents(
        "https://example.com/",
        HTML,
    )

    cleaned = clean_page_content(page)

    assert (
        cleaned.words_removed
        == cleaned.original_word_count - cleaned.word_count
    )

    assert (
        cleaned.characters_removed
        == (
            cleaned.original_character_count
            - cleaned.character_count
        )
    )


def test_cleaner_handles_empty_content():
    page = extract_page_contents(
        "https://example.com/",
        "<html><body></body></html>",
    )

    cleaned = clean_page_content(page)

    assert cleaned.original_word_count == 0
    assert cleaned.original_character_count == 0

    assert cleaned.words_removed == 0
    assert cleaned.characters_removed == 0

    assert cleaned.word_reduction_percent == 0.0
    assert cleaned.character_reduction_percent == 0.0