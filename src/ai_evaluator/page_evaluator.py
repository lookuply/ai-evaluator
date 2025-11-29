"""Page content evaluation using LLM."""

import re
from typing import Any

from pydantic import BaseModel

from ai_evaluator.ollama_client import OllamaClient


class EvaluationResult(BaseModel):
    """Result of page evaluation."""

    url: str
    score: float  # 0.0 to 1.0
    is_useful: bool
    reason: str


class PageEvaluator:
    """Evaluates web page content quality using LLM."""

    def __init__(self, ollama_client: OllamaClient, min_score: float = 0.6) -> None:
        """Initialize page evaluator.

        Args:
            ollama_client: Ollama client for LLM inference
            min_score: Minimum score threshold for usefulness
        """
        self.ollama = ollama_client
        self.min_score = min_score

    async def evaluate(self, content: dict[str, Any]) -> EvaluationResult:
        """Evaluate page content quality.

        Args:
            content: Dictionary with title, text, url, and optional metadata

        Returns:
            Evaluation result with score and reason
        """
        title = content.get("title", "")
        text = content.get("text", "")
        url = content.get("url", "")

        # Handle empty content
        if not title and not text:
            return EvaluationResult(
                url=url, score=0.0, is_useful=False, reason="Empty or no content"
            )

        # Build evaluation prompt
        system_prompt = """You are an expert content evaluator for a search engine.
Evaluate the usefulness and quality of web page content.
Respond with:
SCORE: <0.0-1.0>
REASON: <brief explanation>

Consider:
- Content depth and informativeness
- Writing quality and clarity
- Usefulness to readers
- Presence of spam or excessive ads
"""

        user_prompt = f"""Title: {title}

Content: {text[:2000]}

Evaluate this page content."""

        # Get LLM evaluation
        response = await self.ollama.generate(user_prompt, system=system_prompt)

        # Parse score and reason
        score, reason = self._parse_response(response)

        # Determine usefulness
        is_useful = score >= self.min_score

        return EvaluationResult(url=url, score=score, is_useful=is_useful, reason=reason)

    def _parse_response(self, response: str) -> tuple[float, str]:
        """Parse LLM response to extract score and reason.

        Args:
            response: LLM response text

        Returns:
            Tuple of (score, reason)
        """
        # Try to find score in various formats
        score = 0.5  # default
        reason = response

        # Pattern: SCORE: 0.85 or Score: 0.85
        score_match = re.search(r"score:\s*([\d.]+)", response, re.IGNORECASE)
        if score_match:
            try:
                score = float(score_match.group(1))
                # Normalize if score is > 1 (e.g., "7" from "7/10")
                if score > 1:
                    score = score / 10.0
            except ValueError:
                pass

        # Pattern: 8.5/10 or 7/10
        fraction_match = re.search(r"([\d.]+)/10", response)
        if fraction_match and not score_match:
            try:
                score = float(fraction_match.group(1)) / 10.0
            except ValueError:
                pass

        # Extract reason (text after REASON: or the whole response)
        reason_match = re.search(r"reason:\s*(.+)", response, re.IGNORECASE | re.DOTALL)
        if reason_match:
            reason = reason_match.group(1).strip()
        else:
            # Use whole response as reason, cleaned up
            reason = response.strip()

        # Clamp score to 0-1 range
        score = max(0.0, min(1.0, score))

        return score, reason
