"""Configuration management for Agnes Mini using Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Supports .env file loading and type coercion.
    """

    model_config = SettingsConfigDict(
        env_prefix="AGNES_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API credentials
    api_key: str = ""

    # API endpoints
    base_url: str = "https://api.agnesai.com"

    # Default model names
    chat_model: str = "agnes-2.0-flash"
    image_model: str = "agnes-image-2.1-flash"
    video_model: str = "agnes-video-v2.0"

    # HTTP client settings
    timeout: int = 60
    max_retries: int = 3

    # Video polling settings
    video_poll_interval: int = 5
    video_poll_timeout: int = 600

    # Output directory for generated files
    output_dir: str = "./output"

    # Logging level
    log_level: str = "INFO"

    @property
    def is_mock_mode(self) -> bool:
        """Return True if no API key is configured (Mock mode)."""
        return not bool(self.api_key)


@lru_cache
def get_settings() -> Settings:
    """Get cached Settings singleton.

    Returns:
        A cached Settings instance loaded from environment / .env file.
    """
    return Settings()
