from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup


@dataclass
class ExtractedLink:
    url: str
    text: str = ""
    is_internal: bool = False


@dataclass
class ExtractedImage:
    src: str
    alt: str = ""

    @property
    def has_alt(self) -> bool:
        return bool(self.alt.strip())


@dataclass
class ExtractedForm:
    action: str
    method: str
    input_count: int
    button_count: int


@dataclass
class ExtractedPage:
    url: str
    title: str = ""
    meta_description: str = ""
    canonical_url: str = ""

    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    list_items: list[str] = field(default_factory=list)

    links: list[ExtractedLink] = field(default_factory=list)
    images: list[ExtractedImage] = field(default_factory=list)
    forms: list[ExtractedForm] = field(default_factory=list)

    buttons: list[str] = field(default_factory=list)
    input_types: list[str] = field(default_factory=list)
    navigation_text: list[str] = field(default_factory=list)

    text: str = ""
    word_count: int = 0
    character_count: int = 0
    extraction_method: str = "beautifulsoup"


def _clean_text(value: str) -> str:
    """Normalize whitespace in extracted text."""
    return " ".join(value.split())


def _is_internal(url: str, base_url: str) -> bool:
    """Return True when a URL belongs to the source page's domain."""
    source_host = (urlparse(base_url).hostname or "").lower()
    target_host = (urlparse(url).hostname or "").lower()

    return source_host == target_host


def _extract_with_trafilatura(html: str) -> str:
    """
    Extract main content from HTML using trafilatura.

    Uses trafilatura.extract() with these settings:
    - include_comments=False
    - include_tables=True
    - no_fallback=False
    - favor_precision=True
    - include_formatting=False

    Returns extracted text string.
    Returns empty string if trafilatura returns None
    or raises any exception.
    Never raises — always returns a string.
    """
    try:
        # pyrefly: ignore [missing-import]
        import trafilatura
        result = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
            include_formatting=False,
        )
        return result if result is not None else ""
    except Exception:
        return ""


def _extract_with_beautifulsoup(
    soup: BeautifulSoup,
) -> str:
    """
    Extract main content text from a BeautifulSoup object.

    Extract text from these elements in priority order:
      article tag → main tag → div with class containing
      'content' → div with class containing 'post' →
      div with class containing 'entry' →
      div with class containing 'article' → body tag

    Use .get_text(separator=" ", strip=True) on the
    chosen element.
    Collapse multiple spaces and newlines into single space.
    Return cleaned text string.
    Return empty string if nothing found.
    Never raises — always returns a string.
    """
    try:
        def has_class_part(cls_list, part):
            if not cls_list:
                return False
            if isinstance(cls_list, str):
                return part in cls_list.lower()
            return any(part in c.lower() for c in cls_list)

        target = soup.find("article")
        if not target:
            target = soup.find("main")
        if not target:
            target = soup.find("div", class_=lambda c: has_class_part(c, "content"))
        if not target:
            target = soup.find("div", class_=lambda c: has_class_part(c, "post"))
        if not target:
            target = soup.find("div", class_=lambda c: has_class_part(c, "entry"))
        if not target:
            target = soup.find("div", class_=lambda c: has_class_part(c, "article"))
        if not target:
            target = soup.find("body")

        if not target:
            return ""

        raw_text = target.get_text(separator=" ", strip=True)
        return " ".join(raw_text.split())
    except Exception:
        return ""


def extract_page_contents(
    url: str,
    html: str,
) -> ExtractedPage:
    """Extract structured content and metadata from one HTML page."""

    soup = BeautifulSoup(html, "html.parser")

    # Remove elements that should never contribute to page text.
    for element in soup(["script", "style", "noscript", "template"]):
        element.decompose()

    page = ExtractedPage(url=url)

    # Metadata
    title = soup.find("title")
    if title:
        page.title = _clean_text(title.get_text(" ", strip=True))

    description = soup.find(
        "meta",
        attrs={"name": lambda value: value and value.lower() == "description"},
    )
    if description:
        page.meta_description = _clean_text(
            description.get("content", "")
        )

    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    if canonical and canonical.get("href"):
        page.canonical_url = urljoin(
            url,
            canonical["href"],
        )

    # Headings
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        text = _clean_text(heading.get_text(" ", strip=True))
        if text:
            page.headings.append(text)

    # Paragraphs
    for paragraph in soup.find_all("p"):
        text = _clean_text(paragraph.get_text(" ", strip=True))
        if text:
            page.paragraphs.append(text)

    # List items
    for item in soup.find_all("li"):
        text = _clean_text(item.get_text(" ", strip=True))
        if text:
            page.list_items.append(text)

    # Links
    for anchor in soup.find_all("a", href=True):
        target = urljoin(url, anchor["href"])

        parsed = urlparse(target)

        # Ignore fragment-only links and non-web links.
        if parsed.scheme not in {"http", "https"}:
            continue

        page.links.append(
            ExtractedLink(
                url=target,
                text=_clean_text(anchor.get_text(" ", strip=True)),
                is_internal=_is_internal(target, url),
            )
        )

    # Images
    for image in soup.find_all("img", src=True):
        page.images.append(
            ExtractedImage(
                src=urljoin(url, image["src"]),
                alt=_clean_text(image.get("alt", "")),
            )
        )

    # Forms
    for form in soup.find_all("form"):
        action = urljoin(
            url,
            form.get("action", ""),
        )

        method = form.get("method", "GET").upper()

        input_count = len(form.find_all("input"))
        button_count = len(
            form.find_all(["button", "input"], type="submit")
        )

        page.forms.append(
            ExtractedForm(
                action=action,
                method=method,
                input_count=input_count,
                button_count=button_count,
            )
        )

    # Buttons
    for button in soup.find_all("button"):
        text = _clean_text(button.get_text(" ", strip=True))
        if text:
            page.buttons.append(text)

    # Input types
    for input_element in soup.find_all("input"):
        input_type = input_element.get("type", "text").lower()
        page.input_types.append(input_type)

    # Navigation
    for navigation in soup.find_all("nav"):
        text = _clean_text(navigation.get_text(" ", strip=True))
        if text:
            page.navigation_text.append(text)

    from config import DEFAULT_CONFIG

    min_length = DEFAULT_CONFIG.extraction.min_content_length

    # Try trafilatura first on the original HTML
    trafilatura_text = _extract_with_trafilatura(html)
    trafilatura_words = len(trafilatura_text.split())

    if trafilatura_words >= min_length:
        # Use trafilatura result as main text
        page.text = trafilatura_text
        page.extraction_method = "trafilatura"
    else:
        # Fall back to BeautifulSoup
        bs4_text = _extract_with_beautifulsoup(soup)
        bs4_words = len(bs4_text.split())

        if bs4_words >= min_length:
            page.text = bs4_text
            page.extraction_method = "beautifulsoup"
        else:
            # Both failed
            page.text = bs4_text or trafilatura_text
            page.extraction_method = "failed"

    page.word_count = len(page.text.split())
    page.character_count = len(page.text)

    return page