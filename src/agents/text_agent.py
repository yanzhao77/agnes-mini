"""Text agent wrapping ChatProvider with conversation history."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from src.agents.base import BaseAgent
from src.models.chat import (
    ChatHistory,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
)
from src.providers.chat import ChatProvider
from src.providers.mock_chat import MockChatProvider


class TextAgent(BaseAgent):
    """Agent for text-based conversations."""
    AGENT_TYPE = "text"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._provider: ChatProvider | MockChatProvider = (
            ChatProvider(self.settings) if not self.settings.is_mock_mode
            else MockChatProvider(self.settings)
        )
        self.history = ChatHistory()

    async def chat(self, message: str, system_prompt: str | None = None) -> ChatResponse:
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.extend(self.history.to_api_messages() if self.history.messages else [])
        messages.append(ChatMessage(role="user", content=message))
        request = ChatRequest(model=self.settings.chat_model, messages=messages)
        response = await self._provider.chat(request)
        if response.choices:
            self.history.add_message(ChatMessage(role="user", content=message))
            self.history.add_message(response.choices[0].message)
        return response

    async def chat_stream(self, message: str) -> AsyncGenerator[ChatStreamChunk, None]:
        messages = list(self.history.to_api_messages())
        messages.append(ChatMessage(role="user", content=message))
        request = ChatRequest(model=self.settings.chat_model, messages=messages, stream=True)
        full_content = ""
        async for chunk in self._provider.chat_stream(request):
            if chunk.choices and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
            yield chunk
        self.history.add_message(ChatMessage(role="user", content=message))
        self.history.add_message(ChatMessage(role="assistant", content=full_content or ""))

    async def clear_history(self) -> None:
        self.history.clear()
