"""Shared model types and base classes for Agnes Mini data models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Message role in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """Reason why the model stopped generating."""

    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


class ImageSize(str, Enum):
    """Supported image generation sizes."""

    SQUARE_1024 = "1024x1024"
    LANDSCAPE_1920 = "1920x1080"
    PORTRAIT_1080 = "1080x1920"
    LANDSCAPE_1216 = "1216x832"
    PORTRAIT_832 = "832x1216"


class AspectRatio(str, Enum):
    """Aspect ratio presets for image/video generation."""

    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_3_4 = "3:4"


class VideoStatus(str, Enum):
    """Possible states of a video generation task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoDuration(str, Enum):
    """Video duration options."""

    SHORT = "5"
    MEDIUM = "10"
    STANDARD = "15"
    LONG = "25"


class Usage(BaseModel):
    """Token usage information for a model response."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ErrorDetail(BaseModel):
    """Structured error detail returned by the API."""

    code: str | None = None
    message: str = ""
    type: str | None = None


class ToolCall(BaseModel):
    """A tool call in the model response."""

    id: str = ""
    type: str = "function"
    function: ToolFunction


class ToolFunction(BaseModel):
    """Function details within a tool call."""

    name: str = ""
    arguments: str = "{}"


class FunctionTool(BaseModel):
    """Tool definition for function calling."""

    type: str = "function"
    function: FunctionToolDef


class FunctionToolDef(BaseModel):
    """Function definition within a tool."""

    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
