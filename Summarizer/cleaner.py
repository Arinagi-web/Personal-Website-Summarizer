from __future__ import annotations

from dataclasses import dataclass, field

from Summarizer.extractor import ExtractedPage


@dataclass
class CleanedPage:
    """Represents cleaned and deduplicated webpage content."""

    url: str
    title: str = ""

    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)

    text: str = ""

    word_count: int = 0
    character_count: int = 0

    original_word_count: int = 0
    original_character_count: int = 0

    words_removed: int = 0
    characters_removed: int = 0

    word_reduction_percent: float = 0.0
    character_reduction_percent: float = 0.0


def _deduplicate(values: list[str]) -> list[str]:
    """Remove duplicate strings while preserving their original order."""

    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        normalized = value.strip().replace("\u00b6", "").strip()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(normalized)

    return result


def _calculate_reduction_percent(
    original: int,
    current: int,
) -> float:
    """Calculate the percentage removed from the original value."""

    if original == 0:
        return 0.0

    return ((original - current) / original) * 100.0


def clean_html(html: str) -> str:
    """
    Strip noise from raw HTML before extraction.
    Use BeautifulSoup(html, "html.parser").
    
    Remove these tags entirely (decompose):
      script, style, noscript, template, iframe,
      nav, header, footer, aside, form
    
    Remove elements whose class or id contains ANY
    of these keywords (case-insensitive, check both
    class list joined as string and id attribute):
      ad, advertisement, sidebar, cookie, popup,
      banner, newsletter, subscribe, menu, social,
      share, comment, related, recommended, promo,
      widget, overlay, modal, sticky, toolbar,
      breadcrumb, pagination, tag, label, badge,
      announcement, alert, notice, notification,
      quick-link, quicklink
    
    Return str(soup) after decomposing noise elements.
    Never raise — return original html on any exception.
    """
    try:
        # pyrefly: ignore [missing-import]
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        tags_to_remove = ["script", "style", "noscript", "template", "iframe",
                          "nav", "header", "footer", "aside", "form"]
        for tag in soup(tags_to_remove):
            tag.decompose()
            
        noise_keywords = [
            "ad", "advertisement", "sidebar", "cookie", "popup",
            "banner", "newsletter", "subscribe", "menu", "social",
            "share", "comment", "related", "recommended", "promo",
            "widget", "overlay", "modal", "sticky", "toolbar",
            "breadcrumb", "pagination", "tag", "label", "badge",
            "announcement", "alert", "notice", "notification",
            "quick-link", "quicklink"
        ]
        
        for element in soup.find_all(True):
            class_list = element.get("class", [])
            if isinstance(class_list, list):
                class_str = " ".join(class_list).lower()
            else:
                class_str = str(class_list).lower()
                
            id_str = str(element.get("id", "")).lower()
            
            for keyword in noise_keywords:
                if keyword in class_str or keyword in id_str:
                    element.decompose()
                    break
                    
        import re
        cleaned = str(soup)
        cleaned = cleaned.replace("\u00b6", "")
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned
    except Exception:
        return html



def clean_page_content(
    page: ExtractedPage,
) -> CleanedPage:
    """Clean and deduplicate the meaningful content from an extracted page."""

    headings = _deduplicate(page.headings)
    paragraphs = _deduplicate(page.paragraphs)

    original_text = page.text.strip()

    original_word_count = len(original_text.split())
    original_character_count = len(original_text)

    content_parts = headings + paragraphs
    text = "\n\n".join(content_parts)

    word_count = len(text.split())
    character_count = len(text)

    words_removed = max(
        0,
        original_word_count - word_count,
    )

    characters_removed = max(
        0,
        original_character_count - character_count,
    )

    return CleanedPage(
        url=page.url,
        title=page.title,
        headings=headings,
        paragraphs=paragraphs,
        text=text,
        word_count=word_count,
        character_count=character_count,
        original_word_count=original_word_count,
        original_character_count=original_character_count,
        words_removed=words_removed,
        characters_removed=characters_removed,
        word_reduction_percent=_calculate_reduction_percent(
            original_word_count,
            word_count,
        ),
        character_reduction_percent=_calculate_reduction_percent(
            original_character_count,
            character_count,
        ),
    )