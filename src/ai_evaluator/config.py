"""Configuration for AI Evaluator service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI Evaluator settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Ollama configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b-instruct-q4_K_M"
    ollama_timeout: int = 60

    # Evaluation criteria (hidden server-side for anti-gaming)
    min_content_length: int = 100
    min_quality_score: float = 0.6
    max_ad_ratio: float = 0.3

    # Performance
    evaluation_cache_ttl: int = 3600  # 1 hour


settings = Settings()
