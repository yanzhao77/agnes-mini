"""Tests for ImageAgent."""
from __future__ import annotations

import pytest

from src.agents.image_agent import ImageAgent
from src.config import Settings


@pytest.fixture
def agent():
    return ImageAgent(Settings())


@pytest.mark.asyncio
async def test_image_agent_generate(agent):
    result = await agent.generate("A cat")
    assert len(result.urls) > 0
    assert "mock.agnes.ai" in result.urls[0]


@pytest.mark.asyncio
async def test_image_agent_generate_and_save(agent):
    result = await agent.generate_and_save("A dog", "./output")
    assert len(result.local_paths) > 0


@pytest.mark.asyncio
async def test_image_agent_image_to_image(agent):
    result = await agent.image_to_image("Enhance this", "https://example.com/image.png")
    assert len(result.urls) > 0
