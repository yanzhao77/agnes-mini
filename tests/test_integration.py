"""Integration tests for provider factory, internal tools."""
from __future__ import annotations

import pytest

from src.config import Settings
from src.exceptions import ProviderNotFoundError
from src.internal.dev_skill import analyze_error, gen_agent, gen_provider, gen_test_stub
from src.internal.review_skill import check_architecture
from src.internal.test_skill import gen_mock, gen_test_case
from src.providers.base import create_provider
from src.providers.chat import ChatProvider
from src.providers.image import ImageProvider
from src.providers.mock_chat import MockChatProvider
from src.providers.mock_image import MockImageProvider
from src.providers.mock_video import MockVideoProvider
from src.providers.video import VideoProvider


def test_create_provider_mock_chat():
    p = create_provider("chat", Settings(api_key=""))
    assert isinstance(p, MockChatProvider)


def test_create_provider_mock_image():
    p = create_provider("image", Settings(api_key=""))
    assert isinstance(p, MockImageProvider)


def test_create_provider_mock_video():
    p = create_provider("video", Settings(api_key=""))
    assert isinstance(p, MockVideoProvider)


def test_create_provider_unknown():
    with pytest.raises(ProviderNotFoundError):
        create_provider("unknown")


def test_create_provider_real_chat():
    p = create_provider("chat", Settings(api_key="test-key"))
    assert isinstance(p, ChatProvider)


def test_create_provider_real_image():
    p = create_provider("image", Settings(api_key="test-key"))
    assert isinstance(p, ImageProvider)


def test_create_provider_real_video():
    p = create_provider("video", Settings(api_key="test-key"))
    assert isinstance(p, VideoProvider)


def test_gen_provider_code():
    r = gen_provider("test", "m1", "desc")
    assert "testProvider" in r


def test_gen_agent_code():
    r = gen_agent("test", "desc")
    assert "testAgent" in r


def test_gen_test_stub():
    r = gen_test_stub("MyClass")
    assert "MyClass" in r
    assert "@pytest.mark.asyncio" in r


def test_analyze_error_missing_import():
    r = analyze_error("ModuleNotFoundError: No module named 'xyz'")
    assert r["type"] == "missing_import"


def test_analyze_error_syntax():
    r = analyze_error('SyntaxError: invalid syntax (test.py, line 42)')
    assert r["type"] == "syntax_error"
    assert r["line"] == 42


def test_check_architecture_nonexistent():
    r = check_architecture("/nonexistent/path")
    assert r["pass"] is False


def test_gen_test_case():
    r = gen_test_case("MyService")
    assert "MyService" in r


def test_gen_mock():
    r = gen_mock("Weather")
    assert "MockWeatherProvider" in r
