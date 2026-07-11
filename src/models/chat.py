"""Data models for chat/text interactions with Agnes AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from src.models.common import (
    ErrorDetail,
    FinishReason,
    FunctionTool,
    Role,
    ToolCall,
    Usage,
)


class ImageUrlContent(BaseModel):
    """Image URL content for multimodal messages."""

    url: str
    detail: Optional[str] = None


class MessageContent(BaseModel):
    """A single content item in a message (text or image_url)."""

    type: str = "text"
    text: Optional[str] = None
    image_url: Optional[ImageUrlContent] = None


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str = "user"
    content: Optional[Union[str, List[MessageContent]]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ChatRequest(BaseModel):
    """Request payload for the chat completions API."""

    model: str = "agnes-2.0-flash"
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: bool = False
    tools: Optional[List[FunctionTool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    extra_body: Optional[Dict[str, Any]] = None


class ChatChoice(BaseModel):
    """A single choice in the chat response."""

    index: int = 0
    message: ChatMessage = Field(default_factory=ChatMessage)
    finish_reason: Optional[FinishReason] = None


class ChatResponse(BaseModel):
    """Response from the chat completions API."""

    id: str = ""
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: List[ChatChoice] = Field(default_factory=list)
    usage: Optional[Usage] = None


class DeltaMessage(BaseModel):
    """Delta content in a streaming response."""

    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class StreamChoice(BaseModel):
    """A single streaming choice with delta content."""

    index: int = 0
    delta: DeltaMessage = Field(default_factory=DeltaMessage)
    finish_reason: Optional[FinishReason] = None


class ChatStreamChunk(BaseModel):
    """A single chunk from a streaming chat response."""

    id: str = ""
    object: str = "chat.completion.chunk"
    created: int = 0
    model: str = ""
    choices: List[StreamChoice] = Field(default_factory=list)


class ChatHistory(BaseModel):
    """Accumulated conversation history for an agent."""

    messages: List[ChatMessage] = Field(default_factory=list)
    max_turns: int = 50

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to history, respecting max_turns."""
        self.messages.append(message)
        if len(self.messages) > self.max_turns:
            if self.messages[0].role == "system":
                self.messages = [self.messages[0]] + self.messages[-(self.max_turns - 1):]
            else:
                self.messages = self.messages[-self.max_turns:]

    def to_api_messages(self) -> List[dict]:
        """Convert history to API-compatible message list."""
        return [m.model_dump(exclude_none=True) for m in self.messages]

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
