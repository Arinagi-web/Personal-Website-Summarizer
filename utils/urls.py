from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)


SUPPORTED_SCHEMES = {"http", "https"}


def is_valid_http_url(url: str) -> bool:
    """Return True when the value is a valid HTTP/HTTPS URL."""

    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    return (
        parsed.scheme.lower() in SUPPORTED_SCHEMES
        and bool(parsed.netloc)
    )


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent comparison.

    The normalization intentionally avoids aggressive transformations
    that could change the meaning of a URL.
    """

    if not is_valid_http_url(url):
        raise ValueError(f"Invalid HTTP URL: {url!r}")

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if not hostname:
        raise ValueError(f"URL has no hostname: {url!r}")

    netloc = hostname

    if parsed.port is not None:
        default_port = (
            (scheme == "http" and parsed.port == 80)
            or (scheme == "https" and parsed.port == 443)
        )

        if not default_port:
            netloc = f"{hostname}:{parsed.port}"

    path = parsed.path or "/"

    # Remove a trailing slash except for the root path.
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Sort query parameters for stable comparison.
    query_pairs = parse_qsl(
        parsed.query,
        keep_blank_values=True,
    )
    query = urlencode(sorted(query_pairs))

    return urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            query,
            "",
        )
    )


def resolve_url(base_url: str, relative_url: str) -> str:
    """Resolve a relative URL against a base URL."""

    if not is_valid_http_url(base_url):
        raise ValueError(f"Invalid base URL: {base_url!r}")

    return normalize_url(urljoin(base_url, relative_url))


def is_same_domain(url: str, domain: str) -> bool:
    """
    Check whether a URL belongs to the specified hostname.

    Subdomains are not automatically considered the same domain.
    """

    if not is_valid_http_url(url):
        return False

    hostname = (urlparse(url).hostname or "").lower()

    return hostname == domain.lower().rstrip(".")