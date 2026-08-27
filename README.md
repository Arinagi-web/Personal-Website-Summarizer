# Website Summarizer

A standalone utility that accepts a webpage URL and returns a concise AI-generated summary and key points. Built in Python using Scrapy, Playwright, BeautifulSoup, and the Groq API.

## Features
- Static page summarization via Scrapy
- JS-rendered and bot-protected page support via Playwright
- HTML noise removal (nav, ads, sidebars, scripts)
- Content ranking to maximize AI summary quality
- Groq API integration (free tier, llama-3.1-8b-instant)
- Structured output: summary + 6 key points
- Swappable AI provider via config
- Clean terminal report with metadata footer
- Handles long pages, inaccessible pages, extraction failures

## Architecture

URL → Crawler (Scrapy / Playwright)
    → cleaner.py (strip HTML noise)
    → extractor.py (extract text)
    → ranker.py (rank + cap at 24k chars)
    → analyzer.py (metadata)
    → summarizer.py (Groq API)
    → report.py (terminal output)

## Project Structure

Website-Summarizer/
├── Summarizer/
│   ├── cleaner.py
│   ├── extractor.py
│   ├── ranker.py
│   ├── analyzer.py
│   ├── summarizer.py
│   ├── groq_provider.py
│   ├── report.py
│   ├── run.py
│   └── site.py
├── utils/
├── tests/
├── browser.py
├── config.py
├── crawler.py
├── main.py
├── models.py
└── requirements.txt

## Setup

### Prerequisites
- Python 3.11+
- A free Groq API key from console.groq.com

### Installation
  git clone <repo>
  cd Website-Summarizer
  python -m venv .venv
  .venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  playwright install chromium

### Configuration
  Copy .env.example to .env
  Add your GROQ_API_KEY to .env

## Usage

### Summarize a single page (static):
  python main.py https://en.wikipedia.org/wiki/Flat-file_database

### Summarize a JS-rendered or bot-protected page:
  python main.py https://www.apple.com/iphone/ --browser

### Summarize multiple pages from a site:
  python main.py https://example.com --pages 5

## Example Output

  ═══════════════════════════════════════════
  WEBSITE SUMMARY
  URL   : https://en.wikipedia.org/wiki/Flat-file_database
  Title : Flat-file database - Wikipedia
  ═══════════════════════════════════════════

  SUMMARY
  ───────
  A flat-file database stores each record independently...

  KEY POINTS
  ──────────
  • Each record is stored as a semantically independent unit...
  • Records use delimiter-separated or fixed-width formats...
  • [4 more points]

  ───────────────────────────────────────────
  Words analyzed : 1512
  Extraction     : beautifulsoup
  Model          : groq
  Chunked        : No
  ───────────────────────────────────────────

## Tested Sites

| Site | Type | Method | Status |
|------|------|--------|--------|
| Wikipedia | Content page | Scrapy | ✅ |
| DPU University | Institutional homepage | Scrapy | ✅ |
| Python Docs | Technical documentation | Scrapy | ✅ |
| Martinfowler | Long-form blog | Scrapy | ✅ |
| Apple iPhone | JS-rendered | Playwright | ✅ |
| BBC News | JS-rendered | Playwright | ✅ |

## Configuration

Key settings in config.py:
- max_content_chars: 24000 (chars sent to AI)
- model: llama-3.1-8b-instant (fast, free Groq model)
- temperature: 0.3 (factual, low creativity)
- chunk_size_chars: 24000 (chunking threshold)

To switch AI provider, update AIConfig in config.py.

## Running Tests
  pytest tests/ -v

## License
MIT
