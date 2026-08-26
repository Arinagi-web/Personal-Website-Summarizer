from Summarizer.cleaner import CleanedPage
from Summarizer.ranker import rank_page_content


def make_page() -> CleanedPage:
    return CleanedPage(
        url="https://example.com/",
        title="Example Website",
        headings=[
            "Welcome to Example",
            "Our Mission",
        ],
        paragraphs=[
            "We build useful software for businesses.",
            "Our mission is to make complex technology easier to use.",
            "Contact our team for more information.",
        ],
        text=(
            "Welcome to Example\n\n"
            "Our Mission\n\n"
            "We build useful software for businesses.\n\n"
            "Our mission is to make complex technology easier to use.\n\n"
            "Contact our team for more information."
        ),
        word_count=25,
        character_count=200,
        original_word_count=25,
        original_character_count=200,
    )


def test_rank_page_content_returns_ranked_sections():
    page = make_page()

    ranked = rank_page_content(page)

    assert ranked


def test_ranked_sections_have_required_fields():
    page = make_page()

    ranked = rank_page_content(page)

    for section in ranked:
        assert section.text
        assert section.score >= 0
        assert section.section_type


def test_headings_receive_higher_priority_than_paragraphs():
    page = make_page()

    ranked = rank_page_content(page)

    heading_sections = [
        section
        for section in ranked
        if section.section_type == "heading"
    ]

    paragraph_sections = [
        section
        for section in ranked
        if section.section_type == "paragraph"
    ]

    assert heading_sections
    assert paragraph_sections

    assert max(
        section.score
        for section in heading_sections
    ) > min(
        section.score
        for section in paragraph_sections
    )


def test_ranked_sections_are_sorted_by_score_descending():
    page = make_page()

    ranked = rank_page_content(page)

    scores = [section.score for section in ranked]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_ranker_preserves_section_text():
    page = make_page()

    ranked = rank_page_content(page)

    texts = [section.text for section in ranked]

    assert "Welcome to Example" in texts
    assert "Our Mission" in texts
    assert "We build useful software for businesses." in texts


def test_ranker_respects_max_sections():
    page = make_page()

    ranked = rank_page_content(
        page,
        max_sections=2,
    )

    assert len(ranked) == 2


def test_ranker_handles_empty_page():
    page = CleanedPage(
        url="https://example.com/",
    )

    ranked = rank_page_content(page)

    assert ranked == []