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


def _clean_text(value: str) -> str:
    """Normalize whitespace in extracted text."""
    return " ".join(value.split())


def _is_internal(url: str, base_url: str) -> bool:
    """Return True when a URL belongs to the source page's domain."""
    source_host = (urlparse(base_url).hostname or "").lower()
    target_host = (urlparse(url).hostname or "").lower()

    return source_host == target_host


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

    # Main page text.
    # Navigation is deliberately removed so navigation labels do not
    # pollute the content sent to later summarization stages.
    text_soup = BeautifulSoup(str(soup), "html.parser")

    for element in text_soup(["nav", "script", "style", "noscript", "template"]):
        element.decompose()

    page.text = _clean_text(
        text_soup.get_text(" ", strip=True)
    )

    page.word_count = len(page.text.split())
    page.character_count = len(page.text)

    return page