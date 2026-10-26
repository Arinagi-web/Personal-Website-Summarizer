from __future__ import annotations

import argparse
import sys
from urllib.parse import urlparse

from config import validate_config, ConfigurationError
from models import SummaryResult, PageMetadata
from Summarizer.report import format_report
from Summarizer.run import run
from Summarizer.site import summarize_site
from crawler import crawl
from browser import fetch_with_browser


def main() -> None:
    """Run the summarizer from the command"""
    
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    parser = argparse.ArgumentParser(
        description="Summarize a website."
    )
    
    parser.add_argument(
        "url",
        help="Website URL to summarize.",
    )
    
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Use Playwright instead of Scrapy. Use for JS-heavy pages.",
    )
    
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Maximum number of pages to crawl (default 1).",
    )

    parser.add_argument(
        "--summary-sentences",
        type=int,
        default=None,
        help=(
            "Number of sentences for the summary "
            "(default: 3-5). "
            "Cannot be used with --summary-words."
        ),
    )

    parser.add_argument(
        "--summary-words",
        type=int,
        default=None,
        help=(
            "Approximate word count for the summary "
            "(default: 3-5 sentences). "
            "Cannot be used with --summary-sentences."
        ),
    )

    parser.add_argument(
        "--key-points",
        type=int,
        default=None,
        help="Number of key points to generate (default: 6).",
    )

    args = parser.parse_args()

    try:
        parsed_url = urlparse(args.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f"Invalid URL format: {args.url}. Must start with http:// or https://")
            sys.exit(1)

        if args.summary_sentences and args.summary_words:
            print(
                "Error: --summary-sentences and "
                "--summary-words cannot be used together."
            )
            sys.exit(1)

        if args.summary_sentences is not None and args.summary_sentences < 1:
            print("Error: --summary-sentences must be at least 1.")
            sys.exit(1)

        if args.summary_words is not None and args.summary_words < 10:
            print("Error: --summary-words must be at least 10.")
            sys.exit(1)

        if args.key_points is not None and args.key_points < 1:
            print("Error: --key-points must be at least 1.")
            sys.exit(1)

        validate_config()

        if args.pages > 1:
            results = summarize_site(
                site_url=args.url,
                max_pages=args.pages,
                max_depth=None,
            )
            for summary, metadata in results:
                print(format_report(summary, metadata, summary.url))
                print("\n")
        else:
            print(f"🔍 Fetching {args.url}...")

            if args.browser:
                print("🌐 Using browser (Playwright)...")
                html = fetch_with_browser(args.url)
                if not html:
                    result = SummaryResult(
                        url=args.url,
                        error="Browser could not fetch this page. "
                              "The site may have strong bot "
                              "protection or require login.",
                    )
                    print(format_report(
                        result,
                        PageMetadata(url=args.url),
                        args.url,
                    ))
                    sys.exit(1)
            else:
                crawl_result = crawl(
                    args.url,
                    max_pages=1,
                    max_depth=0,
                )
    
                if args.url not in crawl_result.pages:
                    result = SummaryResult(
                        url=args.url,
                        error="Page could not be fetched. "
                              "The site may be blocking automated "
                              "requests. Try the --browser flag.",
                    )
                    print(format_report(
                        result,
                        PageMetadata(url=args.url),
                        args.url,
                    ))
                    sys.exit(1)
    
                html = crawl_result.pages[args.url]
            
            print("📄 Extracting content...")
            
            if args.summary_sentences:
                print(f"📝 Summary: {args.summary_sentences} sentences")
            elif args.summary_words:
                print(f"📝 Summary: ~{args.summary_words} words")
            if args.key_points:
                print(f"🔑 Key points: {args.key_points}")
            
            summary, metadata = run(
                args.url,
                html,
                summary_sentences=args.summary_sentences,
                summary_words=args.summary_words,
                key_points=args.key_points,
            )
            
            if not summary.success:
                print("Warning: Extraction or summarization failed.")
            else:
                print(f"Extraction method: {metadata.extraction_method}, Words: {metadata.word_count}")
                print(f"🤖 Summarizing with {summary.model_used}...")

            print(format_report(summary, metadata, args.url))

    except ConfigurationError as exc:
        print(f"Configuration Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting cleanly.")
        sys.exit(130)


if __name__ == "__main__":
    main()
