# Website Summarizer

A Python-based website analysis and summarization project that crawls a website, extracts its content and structure, and prepares the foundation for generating a clear, useful summary of the entire site.

> **Status:** Early development — crawler and analysis foundation are in place; summarization capabilities are being built.

## Overview

Website Summarizer is designed to turn a website URL into an understandable overview of the website.

Instead of manually visiting every page, the application will:

1. Crawl the website.
2. Discover relevant pages and links.
3. Extract useful page content.
4. Analyze the website's structure and content.
5. Generate summaries for individual pages.
6. Combine those results into an overall website summary.
7. Present the information as a structured report.

### Planned output

A completed summary will provide information such as:

* Website purpose
* Target audience
* Main products or services
* Important topics and keywords
* Site structure and navigation
* Individual page summaries
* Important links and information
* Overall website summary

## Architecture

The project is built around the existing crawling infrastructure:

```text
                    Website URL
                         │
                         ▼
                    ┌─────────┐
                    │ Crawler │
                    └────┬────┘
                         │
                         ▼
                Discovered Pages
                         │
                         ▼
              ┌──────────────────┐
              │ Content Extractor │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Website Analyzer │
              └────────┬─────────┘
                       │
                       ▼
                ┌─────────────┐
                │ Summarizer  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │    Report   │
                └─────────────┘
```

## Project Structure

```text
Website-Summarizer/
│
├── Summarizer/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── extractor.py
│   ├── report.py
│   └── summarizer.py
│
├── browser.py
├── config.py
├── crawler.py
├── crawler_worker.py
├── models.py
│
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   └── urls.py
│
├── requirements.txt
└── README.md
```

### Core components

#### `crawler.py`

Responsible for discovering and collecting pages from a website while respecting crawl boundaries and configured limits.

#### `crawler_worker.py`

Supports the crawling workflow and page processing.

#### `browser.py`

Provides browser-related functionality for websites that require rendered-page access.

#### `models.py`

Contains the data structures used to represent crawled pages and analysis results.

#### `Summarizer/extractor.py`

Responsible for converting raw HTML into clean, useful website content.

#### `Summarizer/analyzer.py`

Analyzes extracted content and identifies relationships, structure, and important information across the website.

#### `Summarizer/summarizer.py`

The main summarization layer. This will transform analyzed website information into concise human-readable summaries.

#### `Summarizer/report.py`

Responsible for assembling the analysis and summaries into a structured final report.

## Goals

The project aims to provide a summarization system that can understand a website as a **whole**, rather than simply summarizing one HTML page.

The long-term goal is to make the workflow as simple as:

```text
Enter URL
   ↓
Crawl
   ↓
Analyze
   ↓
Summarize
   ↓
Understand the website
```

## Development

### Requirements

* Python 3.x
* A virtual environment is recommended

### Installation

Clone the repository:

```bash
git clone https://github.com/Arinagi-web/Website-Summarizer.git
cd Website-Summarizer
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Current Development Plan

### Phase 1 — Crawling Foundation

* [x] Website crawling
* [x] Page discovery
* [x] URL handling
* [x] Crawl result models
* [x] Browser support

### Phase 2 — Content Understanding

* [ ] Clean HTML extraction
* [ ] Heading extraction
* [ ] Paragraph extraction
* [ ] Navigation analysis
* [ ] Metadata extraction
* [ ] Content deduplication

### Phase 3 — Website Analysis

* [ ] Page classification
* [ ] Site structure analysis
* [ ] Important-content detection
* [ ] Key topic extraction
* [ ] Website purpose detection
* [ ] Target-audience analysis

### Phase 4 — Summarization

* [ ] Individual page summaries
* [ ] Website-wide summary
* [ ] Key information extraction
* [ ] Structured summary generation

### Phase 5 — Presentation

* [ ] CLI interface
* [ ] Web interface
* [ ] Interactive website report
* [ ] Crawl progress display
* [ ] Exportable reports

## Design Philosophy

The project separates **crawling**, **content extraction**, **analysis**, and **summarization** rather than sending raw website HTML directly to a language model.

This allows each stage to be tested independently and makes the system easier to optimize and extend.

```text
Raw Website
    ↓
Crawl
    ↓
Raw HTML
    ↓
Clean Content
    ↓
Structured Data
    ↓
Analysis
    ↓
Summary
```

## Future Possibilities

The architecture can eventually support additional website intelligence features, including:

* Website structure visualization
* Automatic page categorization
* SEO-oriented content analysis
* Accessibility insights
* Technology detection
* Broken-link detection
* Content quality analysis
* Website comparison
* Automatic documentation generation
* AI-powered question answering about a website

## License

No license has been selected yet. This project is currently under private development.
