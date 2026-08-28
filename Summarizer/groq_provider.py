from __future__ import annotations

# pyrefly: ignore [missing-import]
import httpx

from config import DEFAULT_CONFIG


def _parse_groq_response(
    raw: str,
) -> tuple[str, list[str]]:
    """
    Parse the structured AI response.
    Extract SUMMARY: line as summary string.
    Extract lines starting with "- " after KEY POINTS:
    as key_points list (strip the "- " prefix).
    Return ("", []) if parsing fails rather than raising.
    """
    try:
        lines = raw.strip().splitlines()
        summary = ""
        key_points = []
        parsing_points = False

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.startswith("SUMMARY:"):
                summary = line_str[len("SUMMARY:"):].strip()
            elif line_str.startswith("KEY POINTS:"):
                parsing_points = True
            elif parsing_points and line_str.startswith("-"):
                point = line_str.lstrip("-").strip()
                if point:
                    key_points.append(point)
            elif not parsing_points and summary and not line_str.startswith("-"):
                # Append multi-line summary if it spills over (robustness)
                summary += " " + line_str

        return summary.strip(), key_points
    except Exception:
        return "", []


def summarize_with_groq(
    text: str,
    url: str = "",
    summary_sentences: int | None = None,
    summary_words: int | None = None,
    key_points: int | None = None,
) -> tuple[str, list[str]]:
    """
    Summarize text using the Groq API.
    Raises exceptions on missing API key, HTTP errors, or malformed responses.
    """
    config = DEFAULT_CONFIG.ai

    if not config.api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    if summary_words is not None:
        summary_instruction = f"approximately {summary_words} words"
    elif summary_sentences is not None:
        summary_instruction = f"{summary_sentences} sentences"
    else:
        summary_instruction = "3-5 sentences"

    if key_points is not None:
        points_count = key_points
    else:
        points_count = DEFAULT_CONFIG.ai.default_key_points

    points_template = "\n".join(
        f"- <key point {i}>"
        for i in range(1, points_count + 1)
    )

    system = (
        "You are a precise webpage summarizer. "
        "Always respond in this exact format and "
        "nothing else:\n\n"
        f"SUMMARY: <{summary_instruction} covering "
        "the main definition, key concepts, historical "
        "context if present, and primary examples "
        "from the content>\n\n"
        f"KEY POINTS:\n"
        f"{points_template}\n\n"
        "Rules:\n"
        "- Be factual, use only the provided content\n"
        "- Each key point must be a complete specific sentence\n"
        "- Do not number the key points\n"
        "- Do not add text before SUMMARY: or after "
        "last point"
    )

    user = f"Summarize this webpage content.\nURL: {url}\n\n{text}"

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_output_tokens,
    }

    with httpx.Client(timeout=config.request_timeout) as client:
        response = client.post(
            config.base_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data or not isinstance(data, dict):
            raise ValueError("Malformed response from Groq: not a JSON object")
            
        choices = data.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            raise ValueError("Malformed response from Groq: missing or empty 'choices'")
            
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ValueError("Malformed response from Groq: choice is not an object")
            
        message = first_choice.get("message")
        if not message or not isinstance(message, dict):
            raise ValueError("Malformed response from Groq: missing or invalid 'message'")
            
        content = message.get("content")
        
        if content is None or not isinstance(content, str) or not content.strip():
            raise ValueError("Malformed response from Groq: missing or empty 'content'")
            
        return _parse_groq_response(content.strip())
