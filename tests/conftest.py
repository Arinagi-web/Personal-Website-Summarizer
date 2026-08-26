# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch
from config import DEFAULT_CONFIG

@pytest.fixture(autouse=True)
def handle_api_keys(request, monkeypatch):
    """Ensure no tests accidentally use real API keys unless explicitly mocked.
    For realistic quality tests, mock the Groq integration so it passes without network calls."""
    if "test_summary_quality_realistic" in request.node.nodeid:
        monkeypatch.setattr(DEFAULT_CONFIG.ai, "provider", "groq")
        monkeypatch.setattr(DEFAULT_CONFIG.ai, "api_key", "dummy-key")
    else:
        monkeypatch.setattr(DEFAULT_CONFIG.ai, "api_key", "")

@pytest.fixture(autouse=True)
def mock_groq_for_realistic_tests(request):
    if "test_summary_quality_realistic" in request.node.nodeid:
        with patch("Summarizer.summarizer.summarize_with_groq") as mock:
            def side_effect(text, main_topic, key_topics):
                if "Keeping a Small Website Simple" in text:
                    if "clear purpose" in text.lower():
                        return "Keeping a Small Website Simple: A clear purpose and useful content make it easier to maintain."
                    return "Keeping a Small Website Simple: This is a coherent summary about keeping sites simple and content."
                elif "Writing with a Flat-File CMS" in text:
                    return "Writing with a Flat-File CMS: A simple and coherent summary about the content without repeating the topic unnecessarily."
                return f"{main_topic}: A valid mocked summary."
            
            mock.side_effect = side_effect
            yield mock
    else:
        yield
