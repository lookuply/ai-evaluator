"""Tests for Ollama client."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from ai_evaluator.ollama_client import OllamaClient


@pytest.fixture
def client() -> OllamaClient:
    """Create Ollama client."""
    return OllamaClient(base_url="http://test-ollama:11434", model="llama3.1:test")


@pytest.mark.asyncio
async def test_generate_success(client: OllamaClient) -> None:
    """Test successful text generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "llama3.1:test",
        "response": "This is a test response",
        "done": True,
    }
    mock_response.raise_for_status = MagicMock()

    client.client.post = AsyncMock(return_value=mock_response)

    result = await client.generate("Test prompt")

    assert result == "This is a test response"
    client.client.post.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_system_prompt(client: OllamaClient) -> None:
    """Test generation with system prompt."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "llama3.1:test",
        "response": "Evaluated response",
        "done": True,
    }
    mock_response.raise_for_status = MagicMock()

    client.client.post = AsyncMock(return_value=mock_response)

    result = await client.generate("Test", system="You are an evaluator")

    assert result == "Evaluated response"
    # Verify system prompt was included in request
    call_args = client.client.post.call_args
    assert "system" in call_args.kwargs["json"]


@pytest.mark.asyncio
async def test_generate_timeout(client: OllamaClient) -> None:
    """Test handling timeout errors."""
    client.client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    with pytest.raises(httpx.TimeoutException):
        await client.generate("Test prompt")


@pytest.mark.asyncio
async def test_generate_connection_error(client: OllamaClient) -> None:
    """Test handling connection errors."""
    client.client.post = AsyncMock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    with pytest.raises(httpx.ConnectError):
        await client.generate("Test prompt")


@pytest.mark.asyncio
async def test_generate_empty_response(client: OllamaClient) -> None:
    """Test handling empty response."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "llama3.1:test",
        "response": "",
        "done": True,
    }
    mock_response.raise_for_status = MagicMock()

    client.client.post = AsyncMock(return_value=mock_response)

    result = await client.generate("Test prompt")

    assert result == ""


@pytest.mark.asyncio
async def test_health_check_success(client: OllamaClient) -> None:
    """Test health check when Ollama is available."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()

    client.client.get = AsyncMock(return_value=mock_response)

    result = await client.health_check()

    assert result is True


@pytest.mark.asyncio
async def test_health_check_failure(client: OllamaClient) -> None:
    """Test health check when Ollama is unavailable."""
    client.client.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

    result = await client.health_check()

    assert result is False
