from __future__ import annotations

from models import SummaryResult, PageMetadata
from Summarizer.analyzer import analyze_page_content
from Summarizer.cleaner import clean_page_content, clean_html
from Summarizer.extractor import extract_page_contents
from Summarizer.ranker import rank_page_content
from Summarizer.summarizer import summarize_page
from utils.logging import get_logger

logger = get_logger(__name__)

def run(
    url: str,
    html: str,
) -> tuple[SummaryResult, PageMetadata]:
    """Orchestrate the full pipeline for ONE page."""

    try:
        logger.info(f"Extracting content from {url}")
        
        cleaned_html = clean_html(html)
        
        extracted = extract_page_contents(
            url,
            cleaned_html,
        )

        cleaned = clean_page_content(extracted)

        ranked = rank_page_content(cleaned)

        analysis = analyze_page_content(
            title=cleaned.title,
            headings=cleaned.headings,
            paragraphs=cleaned.paragraphs,
            list_items=[],
        )

        ranked_text = "\n\n".join(
            section.text
            for section in ranked
        )

        summary = summarize_page(
            title=analysis.title,
            main_topic=analysis.main_topic,
            key_topics=analysis.key_topics,
            text=ranked_text,
            url=url,
        )

        word_count = extracted.word_count
        metadata = PageMetadata(
            url=url,
            title=analysis.title,
            word_count=word_count,
            extraction_method="beautifulsoup"
        )

        return summary, metadata

    except Exception as exc:
        logger.error(f"Failed to summarize {url}: {exc}")
        return SummaryResult(
            url=url,
            error=str(exc),
        ), PageMetadata(url=url)