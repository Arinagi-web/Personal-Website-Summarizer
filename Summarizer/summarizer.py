from __future__ import annotations

import re

from config import DEFAULT_CONFIG
from models import SummaryResult
from Summarizer.groq_provider import summarize_with_groq


def _split_sentences(text: str) -> list[str]:
    """Split normalized text into sentence-like units."""

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def _deduplicate_sentences(
    sentences: list[str],
) -> list[str]:
    """Remove duplicate sentences while preserving order."""

    seen: set[str] = set()
    result: list[str] = []

    for sentence in sentences:
        normalized = sentence.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(sentence)

    return result


def _chunk_text(
    text: str,
    chunk_size: int,
) -> list[str]:
    """Split text into chunks no larger than the configured size."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for sentence in _split_sentences(text):
        sentence_length = len(sentence)

        if current and current_length + 1 + sentence_length > chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_length = 0

        current.append(sentence)

        if current_length:
            current_length += 1

        current_length += sentence_length

    if current:
        chunks.append(" ".join(current))

    return chunks


def _summarize_text(
    text: str,
    main_topic: str,
    key_topics: list[str] | None = None,
) -> str:
    """Create a concise deterministic topic-aware summary."""

    sentences = _split_sentences(text)
    sentences = _deduplicate_sentences(sentences)

    topics = [
        topic.strip().lower()
        for topic in (key_topics or [])
        if topic.strip()
    ]

    if len(sentences) <= 3:
        selected = sentences
    else:
        scored: list[tuple[int, int, str]] = []

        for index, sentence in enumerate(sentences):
            normalized = sentence.lower()

            topic_matches = sum(
                1
                for topic in topics
                if topic in normalized
            )

            scored.append(
                (
                    topic_matches,
                    -index,
                    sentence,
                )
            )

        scored.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )

        relevant = [
            item[2]
            for item in scored
            if item[0] > 0
        ]

        if relevant:
            selected_sentences = relevant[:3]
        else:
            selected_sentences = [
                item[2]
                for item in scored[:3]
            ]

        selected_set = set(selected_sentences)

        # Restore original reading order.
        selected = [
            sentence
            for sentence in sentences
            if sentence in selected_set
        ]

    parts: list[str] = []

    topic = main_topic.strip()

    if topic:
        parts.append(f"{topic}:")

    parts.extend(selected)

    return " ".join(parts)


def _deterministic_summarize_page(
    title: str,
    main_topic: str,
    key_topics: list[str],
    text: str,
    url: str = "",
) -> SummaryResult:
    """Create a deterministic extractive summary from page content."""

    if not text.strip():
        return SummaryResult(
            url=url,
            error="No meaningful content available for summarization.",
            input_chars=0,
        )

    clean_text = " ".join(text.split())
    input_chars = len(text)

    chunk_size = DEFAULT_CONFIG.ai.chunk_size_chars

    chunks = _chunk_text(
        clean_text,
        chunk_size,
    )

    was_chunked = len(chunks) > 1

    if was_chunked:
        chunk_summaries = [
            _summarize_text(
                chunk,
                main_topic,
                key_topics,
            )
            for chunk in chunks
        ]

        # Deduplicate sentences across chunk summaries.
        summary_sentences = []

        for chunk_summary in chunk_summaries:
            sentences = _split_sentences(chunk_summary)

            for sentence in sentences:
                if sentence not in summary_sentences:
                    summary_sentences.append(sentence)

        # Keep the final result concise even when many chunks exist.
        if main_topic.strip():
            summary_parts = [f"{main_topic.strip()}:"]
        else:
            summary_parts = []

        summary_parts.extend(summary_sentences[:6])

        summary = " ".join(summary_parts)

    else:
        summary = _summarize_text(
            clean_text,
            main_topic,
            key_topics,
        )

    key_points = [
        topic.strip()
        for topic in key_topics
        if topic.strip()
    ]

    return SummaryResult(
        url=url,
        summary=summary,
        key_points=key_points,
        model_used="deterministic",
        input_chars=input_chars,
        was_chunked=was_chunked,
    )


def summarize_page(
    title: str,
    main_topic: str,
    key_topics: list[str],
    text: str,
    url: str = "",
    summary_sentences: int | None = None,
    summary_words: int | None = None,
    key_points: int | None = None,
) -> SummaryResult:
    """Orchestrate AI summarization with deterministic fallback."""

    if not text.strip():
        return SummaryResult(
            url=url,
            error="No meaningful content available for summarization.",
            input_chars=0,
        )

    config = DEFAULT_CONFIG.ai
    if config.provider.lower() == "groq" and config.api_key:
        try:
            clean_text = " ".join(text.split())
            input_chars = len(text)
            chunk_size = config.chunk_size_chars

            chunks = _chunk_text(clean_text, chunk_size)
            was_chunked = len(chunks) > 1

            if not was_chunked:
                summary_text, key_points_result = summarize_with_groq(
                    clean_text,
                    url,
                    summary_sentences=summary_sentences,
                    summary_words=summary_words,
                    key_points=key_points,
                )
            else:
                chunk_summaries = []
                import time
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        time.sleep(12)
                    chunk_text, _ = summarize_with_groq(chunk, url)
                    chunk_summaries.append(chunk_text)
                
                synthesis_text = "\n\n".join(chunk_summaries)
                time.sleep(12)
                summary_text, key_points_result = summarize_with_groq(
                    synthesis_text,
                    url,
                    summary_sentences=summary_sentences,
                    summary_words=summary_words,
                    key_points=key_points,
                )

            topic = main_topic.strip()
            if topic and not summary_text.startswith(topic):
                summary_text = f"{topic}: {summary_text}"

            return SummaryResult(
                url=url,
                summary=summary_text,
                key_points=key_points_result,
                model_used="groq",
                input_chars=input_chars,
                was_chunked=was_chunked,
            )
        except Exception:
            pass

    return SummaryResult(
        url=url,
        error=(
            "AI summarization failed. "
            "If this was a rate limit error, "
            "please wait a moment and try again."
        ),
        input_chars=len(text),
    )
