import json
from datetime import datetime, timezone
from pathlib import Path
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from Summarizer.run import run

SUMMARIES_DIR = Path("summaries")

app = FastAPI(title="Website Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    html: str
    url: str = ""

def url_to_cache_path(url: str) -> Path:
    """Convert a URL to its cache file path."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    # Remove leading/trailing slashes, split path
    path = parsed.path.strip("/")
    if not path:
        return SUMMARIES_DIR / "index.json"
    parts = [p for p in path.split("/") if p]
    filename = "--".join(parts) + ".json"
    return SUMMARIES_DIR / filename

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/summarize")
def summarize(request: SummarizeRequest) -> dict:
    """Summarize HTML content with cache support."""
    try:
        # Check cache first
        cache_path = url_to_cache_path(request.url)

        if cache_path.exists():
            cached = json.loads(
                cache_path.read_text(encoding="utf-8")
            )
            # If cached result has an error, don't
            # return it — regenerate instead
            if cached.get("summary"):
                cached["from_cache"] = True
                cached["success"] = True
                return cached

        # Cache miss — run pipeline
        summary, metadata = run(
            request.url,
            request.html,
        )

        if not summary.success:
            return {
                "success": False,
                "error": summary.error or
                         "Summarization failed.",
            }

        result = {
            "success": True,
            "from_cache": False,
            "summary": summary.summary,
            "key_points": summary.key_points,
            "title": metadata.title,
            "word_count": metadata.word_count,
            "language": metadata.language,
            "is_english": metadata.is_english,
            "extraction_method":
                metadata.extraction_method,
            "model_used": summary.model_used,
            "was_chunked": summary.was_chunked,
        }

        # Save to cache for next time
        SUMMARIES_DIR.mkdir(exist_ok=True)
        cache_path.write_text(
            json.dumps(
                {**result,
                 "url": request.url,
                 "generated_at": datetime.now(
                     timezone.utc
                 ).isoformat()},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return result

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

@app.get("/knowledge-base")
def knowledge_base() -> dict:
    """Return all cached page summaries for chatbot."""
    pages = []
    if SUMMARIES_DIR.exists():
        for json_file in SUMMARIES_DIR.glob("*.json"):
            try:
                data = json.loads(
                    json_file.read_text(
                        encoding="utf-8"
                    )
                )
                if data.get("summary"):
                    pages.append(data)
            except Exception:
                continue
    return {"pages": pages, "count": len(pages)}

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
