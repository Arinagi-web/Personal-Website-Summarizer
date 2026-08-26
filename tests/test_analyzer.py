from Summarizer.analyzer import analyze_page_content


def test_analyzer_extracts_main_topic():
    result = analyze_page_content(
        title="About Our Company",
        headings=[
            "About Our Company",
            "Our Mission",
        ],
        paragraphs=[
            "We build useful software for businesses.",
            "Our mission is to make complex technology easier to use.",
        ],
        list_items=[
            "Software development",
            "Technology consulting",
        ],
    )

    assert result.main_topic == "About Our Company"


def test_analyzer_collects_key_topics():
    result = analyze_page_content(
        title="About Our Company",
        headings=[
            "About Our Company",
            "Our Mission",
        ],
        paragraphs=[
            "We build useful software for businesses.",
            "Our mission is to make complex technology easier to use.",
        ],
        list_items=[
            "Software development",
            "Technology consulting",
        ],
    )

    assert "Our Mission" in result.key_topics


def test_analyzer_counts_content():
    result = analyze_page_content(
        title="Test Page",
        headings=["Introduction", "Features"],
        paragraphs=[
            "This is the first paragraph.",
            "This is the second paragraph.",
        ],
        list_items=["Feature one", "Feature two"],
    )

    assert result.heading_count == 2
    assert result.paragraph_count == 2
    assert result.list_item_count == 2


def test_analyzer_identifies_empty_content():
    result = analyze_page_content(
        title="Empty Page",
        headings=[],
        paragraphs=[],
        list_items=[],
    )

    assert result.is_empty is True


def test_analyzer_identifies_non_empty_content():
    result = analyze_page_content(
        title="Useful Page",
        headings=["Introduction"],
        paragraphs=[
            "This page contains useful information."
        ],
        list_items=[],
    )

    assert result.is_empty is False


def test_analyzer_preserves_title():
    result = analyze_page_content(
        title="My Website",
        headings=[],
        paragraphs=["Some useful content."],
        list_items=[],
    )

    assert result.title == "My Website"


def test_analyzer_produces_content_score():
    result = analyze_page_content(
        title="Good Page",
        headings=["Introduction", "Features"],
        paragraphs=[
            "This page contains useful information.",
            "Here is more information about the product.",
        ],
        list_items=["Feature one", "Feature two"],
    )

    assert 0 <= result.content_score <= 1