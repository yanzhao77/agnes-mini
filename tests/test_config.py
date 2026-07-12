"""Tests for the configuration management module."""

import os

from src.config import Settings, get_settings


def test_settings_defaults():
    """Settings should have sensible defaults."""
    settings = Settings()
    assert settings.base_url == "https://apihub.agnes-ai.com"
    assert settings.chat_model == "agnes-2.0-flash"
    assert settings.image_model == "agnes-image-2.1-flash"
    assert settings.video_model == "agnes-video-v2.0"
    assert settings.timeout == 60
    assert settings.max_retries == 3
    assert settings.video_poll_interval == 5
    assert settings.video_poll_timeout == 600
    assert settings.log_level == "INFO"
    assert settings.output_dir == "./output"


def test_settings_empty_api_key_is_mock_mode():
    """Empty api_key should result in mock mode."""
    settings = Settings(api_key="")
    assert settings.api_key == ""
    assert settings.is_mock_mode is True


def test_settings_with_api_key():
    """Settings with an API key should not be in mock mode."""
    settings = Settings(api_key="test-key-123")
    assert settings.api_key == "test-key-123"
    assert settings.is_mock_mode is False


def test_settings_env_override():
    """Settings should read from environment variables."""
    os.environ["AGNES_API_KEY"] = "env-key-456"
    os.environ["AGNES_BASE_URL"] = "https://custom.api.com"
    settings = Settings()
    assert settings.api_key == "env-key-456"
    assert settings.base_url == "https://custom.api.com"
    del os.environ["AGNES_API_KEY"]
    del os.environ["AGNES_BASE_URL"]


def test_get_settings_singleton():
    """get_settings() should return the same instance each time."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_env_prefix():
    """Settings should use AGNES_ prefix correctly."""
    os.environ["AGNES_LOG_LEVEL"] = "DEBUG"
    os.environ["AGNES_TIMEOUT"] = "120"
    settings = Settings()
    assert settings.log_level == "DEBUG"
    assert settings.timeout == 120
    del os.environ["AGNES_LOG_LEVEL"]
    del os.environ["AGNES_TIMEOUT"]


def test_settings_custom_models():
    """Settings should accept custom model names."""
    settings = Settings(
        chat_model="custom-chat",
        image_model="custom-image",
        video_model="custom-video",
    )
    assert settings.chat_model == "custom-chat"
    assert settings.image_model == "custom-image"
    assert settings.video_model == "custom-video"


def test_settings_video_poll_override():
    """Settings should accept video polling overrides."""
    settings = Settings(video_poll_interval=10, video_poll_timeout=900)
    assert settings.video_poll_interval == 10
    assert settings.video_poll_timeout == 900
