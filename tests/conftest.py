"""Shared fixtures for all tests."""

from __future__ import annotations

import pytest

from src.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Return Settings with an empty API key (Mock mode)."""
    return Settings()


@pytest.fixture
def mock_settings_with_key() -> Settings:
    """Return Settings with a fake API key."""
    return Settings(api_key="sk-test-fake-key-12345")
