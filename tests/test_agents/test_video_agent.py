"""Tests for VideoAgent."""
from __future__ import annotations
import pytest
from src.agents.video_agent import VideoAgent
from src.config import Settings
from src.models.video import VideoPollConfig, VideoRequest


@pytest.fixture
def agent():
    return VideoAgent(Settings())


@pytest.mark.asyncio
async def test_video_agent_generate(agent):
    result = await agent.generate("A drone flying")
    assert result.video_url is not None
    assert "mock.agnes.ai" in result.video_url


@pytest.mark.asyncio
async def test_video_agent_create_and_wait(agent):
    request = VideoRequest(prompt="Test video")
    result = await agent.create_and_wait(request)
    assert result.video_url is not None
