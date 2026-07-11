"""Mock chat provider for development and testing without a real API key."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from src.models.chat import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
    DeltaMessage,
    StreamChoice,
)
from src.models.common import FinishReason, Usage
from src.providers.base import BaseProvider


class MockChatProvider(BaseProvider):
    """Mock chat provider that returns canned responses."""

    PROVIDER_TYPE = "mock_chat"
    DEFAULT_MODEL = "agnes-2.0-flash"

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(settings)
        self._conversation_history: list[dict[str, Any]] = []

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a mock chat response."""
        user_msg = next(
            (m.content for m in request.messages if m.role == "user"),
            "Hello",
        )
        response_text = f"Mock response to: {user_msg}" if user_msg else "Mock response."
        return ChatResponse(
            id="mock-chat-001",
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=response_text,
                    ),
                    finish_reason=FinishReason.STOP,
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

    async def chat_stream(
        self, request: ChatRequest
    ) -> AsyncGenerator[ChatStreamChunk, None]:
        """Return mock streaming chunks."""
        user_msg = next(
            (m.content for m in request.messages if m.role == "user"),
            "Hello",
        )
        response_text = f"Mock streaming: {user_msg}"
        words = response_text.split()
        for i, word in enumerate(words):
            yield ChatStreamChunk(
                id="mock-chunk-001",
                model=request.model,
                choices=[
                    StreamChoice(
                        index=0,
                        delta=DeltaMessage(content=word + " "),
                        finish_reason=None if i < len(words) - 1 else FinishReason.STOP,
                    )
                ],
            )

    async def chat_with_tools(
        self, request: ChatRequest
    ) -> ChatResponse:
        """Return a mock response with tool calls."""
        return ChatResponse(
            id="mock-tool-chat-001",
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content="I'll use a tool for that.",
                    ),
                    finish_reason=FinishReason.TOOL_CALLS,
                )
            ],
            usage=Usage(prompt_tokens=15, completion_tokens=5, total_tokens=20),
        )

    async def chat_with_images(
        self, request: ChatRequest
    ) -> ChatResponse:
        """Return a mock response with image content acknowledgment."""
        return ChatResponse(
            id="mock-image-chat-001",
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content="I can see the image you provided.",
                    ),
                    finish_reason=FinishReason.STOP,
                )
            ],
            usage=Usage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
        )

    async def chat_with_thinking(
        self, request: ChatRequest
    ) -> ChatResponse:
        """Return a mock response with thinking mode."""
        return ChatResponse(
            id="mock-thinking-chat-001",
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content="**Thinking:** Let me reason about this...\n\nFinal answer.",
                    ),
                    finish_reason=FinishReason.STOP,
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=30, total_tokens=40),
        )
