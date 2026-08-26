from Summarizer.extractor import extract_page_contents


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta name="description" content="A test page for the website summarizer.">
    <link rel="canonical" href="/about">
</head>

<body>

<nav>
    <a href="/">Home</a>
    <a href="/about">About</a>
</nav>

<main>
    <h1>About Our Company</h1>
    <h2>Our Mission</h2>

    <p>
        We build useful software for businesses.
    </p>

    <p>
        Our mission is to make complex technology easier to use.
    </p>

    <ul>
        <li>Software development</li>
        <li>Technology consulting</li>
    </ul>

    <p>
        <a href="/contact">Contact Us</a>
    </p>

    <p>
        <a href="https://diablo-six.vercel.app/">External Website</a>
    </p>

    <img src="/logo.png" alt="Company logo">
    <img src="/team.jpg">

    <form action="/submit" method="post">
        <input type="text" name="name">
        <input type="email" name="email">
        <button type="submit">Send</button>
    </form>

    <button>Learn More</button>
</main>

<script>
    console.log("This should not appear in extracted text.");
</script>

</body>
</html>
"""


def test_extracts_title():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert page.title == "Test Page"


def test_extracts_metadata():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert page.meta_description == (
        "A test page for the website summarizer."
    )

    assert page.canonical_url == (
        "https://example.com/about"
    )


def test_extracts_headings():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert page.headings == [
        "About Our Company",
        "Our Mission",
    ]


def test_extracts_paragraphs():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert (
        "We build useful software for businesses."
        in page.paragraphs
    )

    assert (
        "Our mission is to make complex technology easier to use."
        in page.paragraphs
    )


def test_extracts_list_items():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert page.list_items == [
        "Software development",
        "Technology consulting",
    ]


def test_extracts_links():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    urls = [link.url for link in page.links]

    assert "https://example.com/" in urls
    assert "https://example.com/about" in urls
    assert "https://example.com/contact" in urls
    assert "https://diablo-six.vercel.app/" in urls


def test_detects_internal_and_external_links():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    internal_links = [
        link
        for link in page.links
        if link.is_internal
    ]

    external_links = [
        link
        for link in page.links
        if not link.is_internal
    ]

    assert any(
        link.url == "https://example.com/contact"
        for link in internal_links
    )

    assert any(
        link.url == "https://diablo-six.vercel.app/"
        for link in external_links
    )


def test_extracts_images_and_alt_text():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert len(page.images) == 2

    image_with_alt = next(
        image
        for image in page.images
        if image.src.endswith("logo.png")
    )

    image_without_alt = next(
        image
        for image in page.images
        if image.src.endswith("team.jpg")
    )

    assert image_with_alt.has_alt is True
    assert image_with_alt.alt == "Company logo"

    assert image_without_alt.has_alt is False
    assert image_without_alt.alt == ""


def test_extracts_forms():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert len(page.forms) == 1

    form = page.forms[0]

    assert form.action == "https://example.com/submit"
    assert form.method == "POST"
    assert form.input_count == 2
    assert form.button_count == 1


def test_extracts_buttons():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert "Learn More" in page.buttons


def test_extracts_input_types():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert "text" in page.input_types
    assert "email" in page.input_types


def test_extracts_navigation():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert len(page.navigation_text) == 1
    assert "Home" in page.navigation_text[0]
    assert "About" in page.navigation_text[0]


def test_excludes_script_content():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert "This should not appear" not in page.text


def test_calculates_text_statistics():
    page = extract_page_contents(
        "https://example.com/about",
        HTML,
    )

    assert page.word_count > 0
    assert page.character_count > 0
    assert page.character_count == len(page.text)