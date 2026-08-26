from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PageAnalysis:
    """Analysis of the meaningful content found on one webpage."""

    title: str
    main_topic: str
    key_topics: list[str]
    heading_count: int
    paragraph_count: int
    list_item_count: int
    is_empty: bool
    content_score: float


def analyze_page_content(
    title: str,
    headings: list[str],
    paragraphs: list[str],
    list_items: list[str],
) -> PageAnalysis:
    """Analyze extracted page content without performing AI summarization."""

    clean_title = title.strip()

    clean_headings = [
        heading.strip()
        for heading in headings
        if heading.strip()
    ]

    clean_paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    clean_list_items = [
        item.strip()
        for item in list_items
        if item.strip()
    ]

    main_topic = clean_title

    if not main_topic and clean_headings:
        main_topic = clean_headings[0]

    key_topics = clean_headings[1:]

    content_exists = bool(
        clean_headings
        or clean_paragraphs
        or clean_list_items
    )

    content_score = min(
        1.0,
        (
            len(clean_headings) * 0.2
            + len(clean_paragraphs) * 0.1
            + len(clean_list_items) * 0.05
        ),
    )

    if clean_paragraphs:
        content_score = max(content_score, 0.5)

    return PageAnalysis(
        title=clean_title,
        main_topic=main_topic,
        key_topics=key_topics,
        heading_count=len(clean_headings),
        paragraph_count=len(clean_paragraphs),
        list_item_count=len(clean_list_items),
        is_empty=not content_exists,
        content_score=content_score,
    )