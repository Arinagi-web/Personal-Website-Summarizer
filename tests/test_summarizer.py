from Summarizer.summarizer import summarize_page


def test_summarizer_returns_summary_for_meaningful_content():
    result = summarize_page(
        title="About Our Company",
        main_topic="About Our Company",
        key_topics=["Our Mission"],
        text=(
            "We build useful software for businesses. "
            "Our mission is to make complex technology easier to use."
        ),
    )

    assert result.summary
    assert result.success is True


def test_summarizer_preserves_page_url():
    result = summarize_page(
        title="About Our Company",
        main_topic="About Our Company",
        key_topics=["Our Mission"],
        text="We build useful software for businesses.",
        url="https://example.com/about",
    )

    assert result.url == "https://example.com/about"


def test_summarizer_reports_input_character_count():
    text = "We build useful software for businesses."

    result = summarize_page(
        title="About Our Company",
        main_topic="About Our Company",
        key_topics=[],
        text=text,
    )

    assert result.input_chars == len(text)


def test_summarizer_rejects_empty_content():
    result = summarize_page(
        title="Empty Page",
        main_topic="Empty Page",
        key_topics=[],
        text="",
    )

    assert result.success is False
    assert result.error is not None


def test_summarizer_does_not_require_api_call_for_empty_content():
    result = summarize_page(
        title="Empty Page",
        main_topic="Empty Page",
        key_topics=[],
        text="",
    )

    assert result.summary == ""
    assert result.input_chars == 0


def test_summarizer_records_model_used():
    result = summarize_page(
        title="Test Page",
        main_topic="Test Page",
        key_topics=[],
        text="This page contains useful information.",
    )

    assert result.model_used != ""


def test_summarizer_returns_key_points():
    result = summarize_page(
        title="Technology",
        main_topic="Technology",
        key_topics=["Software", "Innovation"],
        text=(
            "We develop software for businesses. "
            "Our products simplify complex technology."
        ),
    )

    assert isinstance(result.key_points, list)