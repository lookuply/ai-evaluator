"""Client for interacting with Ollama API."""

import httpx


class OllamaClient:
    """Client for Ollama LLM API."""

    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        """Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate text using Ollama.

        Args:
            prompt: User prompt
            system: Optional system prompt

        Returns:
            Generated text response

        Raises:
            httpx.TimeoutException: If request times out
            httpx.ConnectError: If connection fails
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def health_check(self) -> bool:
        """Check if Ollama service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = await self.client.get(url)
            response.raise_for_status()
            return True
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
