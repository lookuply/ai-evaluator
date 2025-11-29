"""Tests for page evaluator."""

from unittest.mock import AsyncMock

import pytest

from ai_evaluator.ollama_client import OllamaClient
from ai_evaluator.page_evaluator import EvaluationResult, PageEvaluator


@pytest.fixture
def mock_ollama() -> OllamaClient:
    """Create mock Ollama client."""
    client = AsyncMock(spec=OllamaClient)
    return client


@pytest.fixture
def evaluator(mock_ollama: OllamaClient) -> PageEvaluator:
    """Create page evaluator."""
    return PageEvaluator(ollama_client=mock_ollama)


@pytest.mark.asyncio
async def test_evaluate_high_quality_page(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluating a high-quality page."""
    # Mock LLM response indicating high quality
    mock_ollama.generate = AsyncMock(
        return_value="SCORE: 0.9\nREASON: Well-written, informative content"
    )

    content = {
        "title": "Python Best Practices",
        "text": "This is a comprehensive guide to Python best practices...",
        "url": "https://example.com/python-guide",
    }

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.score >= 0.8
    assert result.is_useful is True
    assert "informative" in result.reason.lower()


@pytest.mark.asyncio
async def test_evaluate_low_quality_page(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluating a low-quality page."""
    mock_ollama.generate = AsyncMock(
        return_value="SCORE: 0.3\nREASON: Thin content, mostly ads"
    )

    content = {
        "title": "Click here",
        "text": "Buy now! Limited offer!",
        "url": "https://example.com/spam",
    }

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.score < 0.6
    assert result.is_useful is False
    assert len(result.reason) > 0


@pytest.mark.asyncio
async def test_evaluate_empty_content(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluating empty content."""
    content = {"title": "", "text": "", "url": "https://example.com/empty"}

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.score == 0.0
    assert result.is_useful is False
    assert "empty" in result.reason.lower() or "no content" in result.reason.lower()


@pytest.mark.asyncio
async def test_evaluate_short_content(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluating very short content."""
    mock_ollama.generate = AsyncMock(
        return_value="SCORE: 0.2\nREASON: Too short to be useful"
    )

    content = {
        "title": "Short",
        "text": "Very short text.",
        "url": "https://example.com/short",
    }

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.is_useful is False


@pytest.mark.asyncio
async def test_evaluate_parse_score_formats(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test parsing different score formats from LLM."""
    test_cases = [
        ("SCORE: 0.85\nGood content", 0.85),
        ("Score: 7/10\nReasonable quality", 0.7),
        ("Quality: 0.6\nMedian quality", 0.6),
        ("8.5/10 - Excellent", 0.85),
    ]

    for llm_response, expected_score in test_cases:
        mock_ollama.generate = AsyncMock(return_value=llm_response)

        content = {
            "title": "Test",
            "text": "Test content",
            "url": "https://example.com/test",
        }

        result = await evaluator.evaluate(content)

        assert result is not None
        assert abs(result.score - expected_score) < 0.1


@pytest.mark.asyncio
async def test_evaluate_multilingual_content(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluating non-English content."""
    mock_ollama.generate = AsyncMock(
        return_value="SCORE: 0.8\nREASON: Quality Slovak content"
    )

    content = {
        "title": "Python tutoriál",
        "text": "Toto je komplexný návod na Python...",
        "url": "https://example.sk/python",
        "language": "sk",
    }

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.score > 0.6
    assert result.is_useful is True


@pytest.mark.asyncio
async def test_evaluate_with_metadata(
    evaluator: PageEvaluator, mock_ollama: OllamaClient
) -> None:
    """Test evaluation includes metadata in result."""
    mock_ollama.generate = AsyncMock(return_value="SCORE: 0.7\nGood article")

    content = {
        "title": "Article",
        "text": "Content here",
        "url": "https://example.com/article",
        "author": "John Doe",
        "date": "2024-01-01",
    }

    result = await evaluator.evaluate(content)

    assert result is not None
    assert result.url == "https://example.com/article"
