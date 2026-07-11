"""Tests for OrchestratorAgent."""
from __future__ import annotations
import pytest
from src.agents.orchestrator import OrchestratorAgent
from src.config import Settings


@pytest.fixture
def orchestrator():
    return OrchestratorAgent(Settings())


@pytest.mark.asyncio
async def test_orchestrator_text(orchestrator):
    result = await orchestrator.run("Hello, how are you?")
    assert result.text is not None


@pytest.mark.asyncio
async def test_orchestrator_image(orchestrator):
    result = await orchestrator.run("generate image of a cat")
    assert len(result.image_urls) > 0


@pytest.mark.asyncio
async def test_orchestrator_video(orchestrator):
    result = await orchestrator.run("generate video of a drone")
    assert len(result.video_urls) > 0


@pytest.mark.asyncio
async def test_orchestrator_detect_intent(orchestrator):
    assert await orchestrator._detect_intent("make image") == "image"
    assert await orchestrator._detect_intent("create video") == "video"
    assert await orchestrator._detect_intent("hello world") == "text"
