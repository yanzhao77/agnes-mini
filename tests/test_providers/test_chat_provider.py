"""Tests for the ChatProvider (mock + real)."""

from __future__ import annotations

import pytest

from src.models.chat import ChatMessage, ChatRequest
from src.models.common import FinishReason
from src.providers.mock_chat import MockChatProvider


@pytest.fixture
def mock_chat():
    return MockChatProvider()


@pytest.mark.asyncio
async def test_mock_chat_basic(mock_chat):
    request = ChatRequest(messages=[ChatMessage(role="user", content="Hello")])
    response = await mock_chat.chat(request)
    assert response.id == "mock-chat-001"
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert "Mock" in response.choices[0].message.content


@pytest.mark.asyncio
async def test_mock_chat_with_empty_messages(mock_chat):
    request = ChatRequest(messages=[])
    response = await mock_chat.chat(request)
    assert response.choices[0].message.content is not None


@pytest.mark.asyncio
async def test_mock_chat_stream(mock_chat):
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Hello")],
        stream=True,
    )
    chunks = []
    async for chunk in mock_chat.chat_stream(request):
        chunks.append(chunk)
    assert len(chunks) > 0
    assert chunks[-1].choices[0].finish_reason == FinishReason.STOP


@pytest.mark.asyncio
async def test_mock_chat_with_tools(mock_chat):
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Use a tool")],
    )
    response = await mock_chat.chat_with_tools(request)
    assert response.choices[0].finish_reason == FinishReason.TOOL_CALLS


@pytest.mark.asyncio
async def test_mock_chat_with_images(mock_chat):
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Describe this")],
    )
    response = await mock_chat.chat_with_images(request)
    assert "image" in response.choices[0].message.content.lower()


@pytest.mark.asyncio
async def test_mock_chat_with_thinking(mock_chat):
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Think about this")],
    )
    response = await mock_chat.chat_with_thinking(request)
    assert "Thinking" in response.choices[0].message.content


@pytest.mark.asyncio
async def test_mock_chat_tracks_usage(mock_chat):
    request = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
    response = await mock_chat.chat(request)
    assert response.usage is not None
    assert response.usage.total_tokens > 0
