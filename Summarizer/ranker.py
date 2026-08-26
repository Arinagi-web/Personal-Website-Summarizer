from __future__ import annotations

from dataclasses import dataclass

from Summarizer.cleaner import CleanedPage
from config import DEFAULT_CONFIG


@dataclass
class RankedSection:
    """A piece of cleaned page content with an importance score."""

    text: str
    score: float
    section_type: str


def rank_page_content(
    page: CleanedPage,
    max_sections: int | None = None,
) -> list[RankedSection]:
    """
    Rank cleaned headings and paragraphs.
    Builds the list in an interleaved order (approximating document order),
    filters out low-value sections, and applies a character cap.
    """
    sections: list[RankedSection] = []

    # 1. Filter paragraphs by word count
    valid_paragraphs = [
        p.strip() for p in page.paragraphs 
        if p.strip() and len(p.split()) >= 15
    ]
    
    valid_headings = [h.strip() for h in page.headings if h.strip()]

    # 2. Build sections interleaved to approximate document order
    interleaved: list[RankedSection] = []
    
    if not valid_headings:
        for p in valid_paragraphs:
            interleaved.append(RankedSection(text=p, score=1.0, section_type="paragraph"))
    elif not valid_paragraphs:
        # If no paragraphs, no headings are kept either because they wouldn't be followed by a paragraph
        pass
    else:
        # Proportionally interleave paragraphs under headings
        ratio = max(1, len(valid_paragraphs) // len(valid_headings))
        p_idx = 0
        
        for h in valid_headings:
            # We only add the heading if there is at least one paragraph left to follow it
            if p_idx < len(valid_paragraphs):
                interleaved.append(RankedSection(text=h, score=2.0, section_type="heading"))
                added_paragraphs = 0
                while added_paragraphs < ratio and p_idx < len(valid_paragraphs):
                    interleaved.append(RankedSection(text=valid_paragraphs[p_idx], score=1.0, section_type="paragraph"))
                    p_idx += 1
                    added_paragraphs += 1
                    
        # Append any remaining paragraphs to the last heading
        while p_idx < len(valid_paragraphs):
            interleaved.append(RankedSection(text=valid_paragraphs[p_idx], score=1.0, section_type="paragraph"))
            p_idx += 1

    # 3. Apply the character cap
    max_chars = DEFAULT_CONFIG.extraction.max_content_chars
    kept: list[RankedSection] = []
    total_chars = 0
    
    for section in interleaved:
        section_len = len(section.text)
        if total_chars + section_len >= max_chars:
            break
        kept.append(section)
        total_chars += section_len
        
    # Apply max_sections if provided
    if max_sections is not None and max_sections >= 0:
        kept = kept[:max_sections]
        
    # 4. Fallback if empty
    if not kept:
        # Fall back to the unfiltered original list with character cap
        fallback: list[RankedSection] = []
        for h in page.headings:
            if h.strip():
                fallback.append(RankedSection(text=h.strip(), score=2.0, section_type="heading"))
        for p in page.paragraphs:
            if p.strip():
                fallback.append(RankedSection(text=p.strip(), score=1.0, section_type="paragraph"))
                
        total_chars = 0
        for section in fallback:
            section_len = len(section.text)
            if total_chars + section_len >= max_chars:
                break
            kept.append(section)
            total_chars += section_len
            
        if not kept and fallback:
            kept.append(fallback[0])
            
        if max_sections is not None and max_sections >= 0:
            kept = kept[:max_sections]

    return kept