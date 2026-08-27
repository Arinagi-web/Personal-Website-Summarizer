from __future__ import annotations
# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from unittest.mock import patch, MagicMock
from Summarizer.groq_provider import summarize_with_groq, _parse_groq_response
# pyrefly: ignore [missing-import]
import httpx

def test_missing_api_key_raises_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = ""
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        with pytest.raises(ValueError, match="GROQ_API_KEY is missing"):
            summarize_with_groq("test content", url="https://example.com")

@patch("Summarizer.groq_provider.httpx.Client")
def test_successful_groq_request(mock_client, monkeypatch):
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = "fake-key-for-testing"
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "SUMMARY: Test summary.\n\nKEY POINTS:\n- Point one.\n- Point two."
                }
            }]
        }
        mock_instance.post.return_value = mock_response
        
        summary, key_points = summarize_with_groq("test content", url="https://example.com")
        
        assert summary == "Test summary."
        assert key_points == ["Point one.", "Point two."]

@patch("Summarizer.groq_provider.httpx.Client")
def test_http_error_raised(mock_client, monkeypatch):
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = "fake-key-for-testing"
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("500", request=MagicMock(), response=mock_response)
        mock_instance.post.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            summarize_with_groq("test content", url="https://example.com")

@patch("Summarizer.groq_provider.httpx.Client")
def test_timeout_raised(mock_client, monkeypatch):
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = "fake-key-for-testing"
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        
        mock_instance.post.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(httpx.TimeoutException):
            summarize_with_groq("test content", url="https://example.com")

@patch("Summarizer.groq_provider.httpx.Client")
def test_malformed_response_raised(mock_client, monkeypatch):
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = "fake-key-for-testing"
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_instance.post.return_value = mock_response
        
        with pytest.raises(ValueError, match="Malformed response from Groq"):
            summarize_with_groq("test content", url="https://example.com")

@patch("Summarizer.groq_provider.httpx.Client")
def test_empty_content_raised(mock_client, monkeypatch):
    with patch("Summarizer.groq_provider.DEFAULT_CONFIG") as mock_config:
        mock_config.ai.api_key = "fake-key-for-testing"
        mock_config.ai.model = "llama-3.1-8b-instant"
        mock_config.ai.base_url = "https://api.groq.com/openai/v1/chat/completions"
        mock_config.ai.temperature = 0.3
        mock_config.ai.request_timeout = 30.0
        mock_config.ai.max_output_tokens = 1000
        
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": ""
                }
            }]
        }
        mock_instance.post.return_value = mock_response
        
        with pytest.raises(ValueError, match="Malformed response from Groq"):
            summarize_with_groq("test content", url="https://example.com")

def test_parse_groq_response_summary():
    content = "SUMMARY: Just a summary.\n\nKEY POINTS:\n- Point 1\n- Point 2"
    summary, key_points = _parse_groq_response(content)
    assert summary == "Just a summary."

def test_parse_groq_response_key_points():
    content = "SUMMARY: Just a summary.\n\nKEY POINTS:\n- Point 1\n- Point 2"
    summary, key_points = _parse_groq_response(content)
    assert key_points == ["Point 1", "Point 2"]

def test_parse_groq_response_bad_input():
    content = "Some random text that doesn't follow the format."
    summary, key_points = _parse_groq_response(content)
    assert summary == ""
    assert key_points == []
