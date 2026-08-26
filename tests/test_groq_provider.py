# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
import httpx
from unittest.mock import patch, MagicMock

from config import DEFAULT_CONFIG
from Summarizer.groq_provider import summarize_with_groq
from Summarizer.summarizer import summarize_page
from models import SummaryResult

@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "provider", "groq")
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "api_key", "test-key")
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "chunk_size_chars", 100)
    return DEFAULT_CONFIG

# Provider Tests

def test_missing_api_key_raises_error(monkeypatch):
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "api_key", "")
    with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
        summarize_with_groq("text", "topic", [])

@patch("httpx.Client.post")
def test_successful_groq_request(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is a summary."}}]
    }
    mock_post.return_value = mock_response
    
    summary = summarize_with_groq("Here is text.", "Topic", ["t1"])
    assert summary == "This is a summary."
    mock_post.assert_called_once()
    
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert "messages" in call_kwargs["json"]
    assert call_kwargs["json"]["model"] == DEFAULT_CONFIG.ai.model

@patch("httpx.Client.post")
def test_http_error_raised(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())
    mock_post.return_value = mock_response
    
    with pytest.raises(httpx.HTTPStatusError):
        summarize_with_groq("text", "topic", [])

@patch("httpx.Client.post")
def test_timeout_raised(mock_post, mock_config):
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    
    with pytest.raises(httpx.TimeoutException):
        summarize_with_groq("text", "topic", [])

@patch("httpx.Client.post")
def test_malformed_response_raised(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.json.return_value = {"bad": "data"}
    mock_post.return_value = mock_response
    
    with pytest.raises(ValueError, match="Malformed"):
        summarize_with_groq("text", "topic", [])

@patch("httpx.Client.post")
def test_empty_content_raised(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "   "}}]
    }
    mock_post.return_value = mock_response
    
    with pytest.raises(ValueError, match="empty 'content'"):
        summarize_with_groq("text", "topic", [])

# Integration Tests

@patch("Summarizer.summarizer.summarize_with_groq")
def test_summarize_page_success(mock_summarize, mock_config):
    mock_summarize.return_value = "AI summary."
    result = summarize_page("Title", "Topic", ["t1"], "Short text.", "http://url")
    
    assert result.model_used == "groq"
    assert result.summary == "Topic: AI summary."
    assert result.was_chunked is False
    assert result.input_chars == len("Short text.")
    assert result.success is True

def test_summarize_page_missing_key_fallback(monkeypatch, mock_config):
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "api_key", "")
    result = summarize_page("Title", "Topic", ["t1"], "Short text. " * 5, "http://url")
    
    assert result.model_used == "deterministic"
    assert result.success is True

@patch("Summarizer.summarizer.summarize_with_groq")
def test_summarize_page_api_failure_fallback(mock_summarize, mock_config):
    mock_summarize.side_effect = ValueError("Error")
    result = summarize_page("Title", "Topic", ["t1"], "Short text. " * 5, "http://url")
    
    assert result.model_used == "deterministic"
    assert result.success is True

@patch("Summarizer.summarizer.summarize_with_groq")
def test_summarize_page_chunking(mock_summarize, mock_config, monkeypatch):
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "chunk_size_chars", 10)
    mock_summarize.return_value = "Chunk summary."
    text = "This text is long enough to chunk. " * 3
    result = summarize_page("Title", "Topic", ["t1"], text, "http://url")
    
    assert result.model_used == "groq"
    assert result.was_chunked is True
    assert result.input_chars == len(text)
    assert mock_summarize.call_count > 1  # multiple chunks + synthesis

@patch("Summarizer.summarizer.summarize_with_groq")
def test_synthesis_failure_fallback(mock_summarize, mock_config, monkeypatch):
    monkeypatch.setattr(DEFAULT_CONFIG.ai, "chunk_size_chars", 10)
    # Fail on the second call (synthesis or chunk)
    mock_summarize.side_effect = ["Chunk summary.", ValueError("Fail")]
    
    text = "This text is long enough to chunk. " * 3
    result = summarize_page("Title", "Topic", ["t1"], text, "http://url")
    
    assert result.model_used == "deterministic"

def test_summarize_page_empty_text():
    result = summarize_page("Title", "Topic", [], "", "http://url")
    assert result.error is not None
    assert result.success is False
