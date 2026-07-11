"""Data models for chat/text interactions with Agnes AI."""

from __future__ import annotations
from typing import Any


from pydantic import BaseModel, Field

from src.models.common import (
    FinishReason,
    FunctionTool,
    ToolCall,
    Usage,
)


class ImageUrlContent(BaseModel):
    """Image URL content for multimodal messages."""

    url: str
    detail: str | None = None


class MessageContent(BaseModel):
    """A single content item in a message (text or image_url)."""

    type: str = "text"
    text: str | None = None
    image_url: ImageUrlContent | None = None


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str = "user"
    content: str | list[MessageContent] | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatRequest(BaseModel):
    """Request payload for the chat completions API."""

    model: str = "agnes-2.0-flash"
    messages: list[ChatMessage]
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    stream: bool = False
    tools: list[FunctionTool] | None = None
    tool_choice: str | dict[str, Any] | None = None
    extra_body: dict[str, Any] | None = None


class ChatChoice(BaseModel):
    """A single choice in the chat response."""

    index: int = 0
    message: ChatMessage = Field(default_factory=ChatMessage)
    finish_reason: FinishReason | None = None


class ChatResponse(BaseModel):
    """Response from the chat completions API."""

    id: str = ""
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: list[ChatChoice] = Field(default_factory=list)
    usage: Usage | None = None


class DeltaMessage(BaseModel):
    """Delta content in a streaming response."""

    role: str | None = None
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class StreamChoice(BaseModel):
    """A single streaming choice with delta content."""

    index: int = 0
    delta: DeltaMessage = Field(default_factory=DeltaMessage)
    finish_reason: FinishReason | None = None


class ChatStreamChunk(BaseModel):
    """A single chunk from a streaming chat response."""

    id: str = ""
    object: str = "chat.completion.chunk"
    created: int = 0
    model: str = ""
    choices: list[StreamChoice] = Field(default_factory=list)


class ChatHistory(BaseModel):
    """Accumulated conversation history for an agent."""

    messages: list[ChatMessage] = Field(default_factory=list)
    max_turns: int = 50

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to history, respecting max_turns."""
        self.messages.append(message)
        if len(self.messages) > self.max_turns:
            if self.messages[0].role == "system":
                self.messages = [self.messages[0]] + self.messages[-(self.max_turns - 1):]
            else:
                self.messages = self.messages[-self.max_turns:]

    def to_api_messages(self) -> list[dict[str, Any]]:
        """Convert history to API-compatible message list."""
        return [m.model_dump(exclude_none=True) for m in self.messages]

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
