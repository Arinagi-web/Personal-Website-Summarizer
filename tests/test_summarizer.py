from Summarizer.summarizer import summarize_page
from unittest.mock import patch


@patch("Summarizer.summarizer.summarize_with_groq")
def test_summarizer_returns_summary_for_meaningful_content(mock_summarize):
    mock_summarize.return_value = ("Test summary.", ["Point 1.", "Point 2."])
    result = summarize_page(
        title="Test Page",
        main_topic="Test Topic",
        key_topics=["topic1", "topic2"],
        text="Valid text that is long enough.",
        url="https://example.com"
    )

    assert result.success is True
    assert result.summary == "Test Topic: Test summary."
    assert result.key_points == ["Point 1.", "Point 2."]


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


@patch("Summarizer.summarizer.summarize_with_groq")
def test_summarizer_records_model_used(mock_summarize):
    mock_summarize.return_value = ("Test summary.", ["Point 1.", "Point 2."])
    result = summarize_page(
        title="Test Page",
        main_topic="Test Topic",
        key_topics=["topic1", "topic2"],
        text="This page contains useful information.",
        url="https://example.com"
    )

    assert result.model_used == "groq"


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