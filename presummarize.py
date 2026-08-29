import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from Summarizer.run import run
from Summarizer.cleaner import clean_html
from Summarizer.extractor import extract_page_contents

WEBSITE_ROOT = Path("LadyIrwin")
SUMMARIES_DIR = Path("LadyIrwin/summaries")
BASE_URL = "http://localhost:3000"
SKIP_FOLDERS = {"_next", "_cdn"}
DELAY_SECONDS = 15

def get_cache_filename(html_file: Path) -> str:
    """Convert HTML file path to cache JSON filename."""
    rel = html_file.relative_to(WEBSITE_ROOT)
    parts = list(rel.parts[:-1])  # exclude index.html
    if not parts:
        return "index.json"
    return "--".join(parts) + ".json"

def get_fake_url(html_file: Path) -> str:
    """Generate a fake localhost URL for the page."""
    rel = html_file.relative_to(WEBSITE_ROOT)
    parts = list(rel.parts[:-1])
    if not parts:
        return BASE_URL + "/"
    return BASE_URL + "/" + "/".join(parts) + "/"

def should_skip(html_file: Path) -> bool:
    """Return True if file is in a folder to skip."""
    parts = set(html_file.parts)
    return bool(parts & SKIP_FOLDERS)

def save_result(
    cache_path: Path,
    summary,
    metadata,
    url: str,
    full_text: str = "",
) -> None:
    """Save summary result to JSON cache file."""
    data = {
        "url": url,
        "title": metadata.title,
        "summary": summary.summary,
        "key_points": summary.key_points,
        "full_text": full_text,
        "language": metadata.language,
        "is_english": metadata.is_english,
        "word_count": metadata.word_count,
        "extraction_method": metadata.extraction_method,
        "model_used": summary.model_used,
        "was_chunked": summary.was_chunked,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }
    cache_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def save_error(
    cache_path: Path,
    url: str,
    error: str,
) -> None:
    """Save error result to JSON cache file."""
    data = {
        "url": url,
        "error": error,
        "success": False,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }
    cache_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate all cached summaries",
    )
    args = parser.parse_args()

    SUMMARIES_DIR.mkdir(exist_ok=True)

    if args.regenerate:
        for json_file in SUMMARIES_DIR.glob("*.json"):
            json_file.unlink()

    all_files = [
        f for f in WEBSITE_ROOT.rglob("*.html")
        if not should_skip(f)
    ]
    all_files.sort()
    total = len(all_files)

    saved = 0
    skipped = 0
    failed = 0
    api_calls = 0

    for index, html_file in enumerate(all_files, 1):
        cache_filename = get_cache_filename(html_file)
        cache_path = SUMMARIES_DIR / cache_filename
        fake_url = get_fake_url(html_file)

        print(f"\nProcessing [{index}/{total}]: {html_file}")

        if cache_path.exists():
            print(f"⚠ Skipped (cached): {cache_path}")
            skipped += 1
            continue

        try:
            html = html_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"✗ Failed to read: {html_file} — {e}")
            failed += 1
            continue

        try:
            summary, metadata = run(fake_url, html)

            if not summary.success:
                print(f"✗ Extraction failed: {html_file}")
                save_error(
                    cache_path,
                    fake_url,
                    summary.error or "No content",
                )
                failed += 1
                # No API call made, no delay needed
                continue

            cleaned_html = clean_html(html)
            extracted = extract_page_contents(fake_url, cleaned_html)
            full_text = extracted.text

            save_result(cache_path, summary, metadata,
                       fake_url, full_text=full_text)
            api_calls += 1
            saved += 1
            print(f"✓ Saved: {cache_path}")

            if index < total:
                for remaining in range(
                    DELAY_SECONDS, 0, -1
                ):
                    print(
                        f"  Waiting {DELAY_SECONDS}s "
                        f"before next page... "
                        f"({remaining}s)",
                        end="\r",
                    )
                    time.sleep(1)
                print(" " * 60, end="\r")

        except Exception as e:
            print(f"✗ Failed: {html_file} — {e}")
            save_error(cache_path, fake_url, str(e))
            failed += 1

    print(f"\n{'='*50}")
    print(f"Done: {saved} saved, {skipped} skipped, "
          f"{failed} failed")
    print(f"Total Groq API calls made: {api_calls}")
    print(
        f"Estimated tokens used: "
        f"~{api_calls * 1500:,} "
        f"({api_calls} x 1500 avg)"
    )

    # Build knowledge base
    print("\nBuilding knowledge base...")
    pages = []
    for json_file in SUMMARIES_DIR.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if data.get("summary"):
                pages.append(data)
        except Exception:
            pass
    kb_path = WEBSITE_ROOT / "knowledge.json"
    kb_path.write_text(json.dumps({"pages": pages, "count": len(pages)}), encoding="utf-8")
    print(f"✓ Saved knowledge base: {kb_path} with {len(pages)} pages")

if __name__ == "__main__":
    main()
