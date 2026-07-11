"""Tests for TextAgent."""
from __future__ import annotations
import pytest
from src.agents.text_agent import TextAgent
from src.config import Settings


@pytest.fixture
def agent():
    return TextAgent(Settings())


@pytest.mark.asyncio
async def test_text_agent_chat(agent):
    response = await agent.chat("Hello")
    assert len(response.choices) > 0
    assert len(agent.history.messages) == 2


@pytest.mark.asyncio
async def test_text_agent_clear_history(agent):
    await agent.chat("Hello")
    assert len(agent.history.messages) == 2
    await agent.clear_history()
    assert len(agent.history.messages) == 0


@pytest.mark.asyncio
async def test_text_agent_stream(agent):
    chunks = []
    async for chunk in agent.chat_stream("Hello"):
        chunks.append(chunk)
    assert len(chunks) > 0
    assert len(agent.history.messages) == 2
