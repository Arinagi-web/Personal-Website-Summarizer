from __future__ import annotations

from models import SummaryResult, PageMetadata


def format_report(
    summary: SummaryResult,
    metadata: PageMetadata | None,
    url: str,
) -> str:
    """Format the final terminal report."""

    lines = []

    if not summary.success:
        lines.append("═══════════════════════════════════════════")
        lines.append("SUMMARY FAILED")
        lines.append(f"URL   : {url}")
        lines.append(f"Error : {summary.error}")
        lines.append("═══════════════════════════════════════════")
        return "\n".join(lines)

    title = metadata.title if metadata and metadata.title else "N/A"
    
    lines.append("═══════════════════════════════════════════")
    lines.append("WEBSITE SUMMARY")
    lines.append(f"URL   : {url}")
    lines.append(f"Title : {title}")
    lines.append("═══════════════════════════════════════════")
    lines.append("")
    lines.append("SUMMARY")
    lines.append("───────")
    lines.append(summary.summary)
    
    if summary.key_points:
        lines.append("")
        lines.append("KEY POINTS")
        lines.append("──────────")
        for point in summary.key_points:
            lines.append(f"• {point}")

    words = metadata.word_count if metadata else 0
    extraction = metadata.extraction_method if metadata else "N/A"
    chunked_str = "Yes" if summary.was_chunked else "No"

    lines.append("")
    lines.append("───────────────────────────────────────────")
    lines.append(f"Words analyzed : {words}")
    lines.append(f"Extraction     : {extraction}")
    lines.append(f"Model          : {summary.model_used}")
    lines.append(f"Chunked        : {chunked_str}")
    lines.append("───────────────────────────────────────────")

    return "\n".join(lines)