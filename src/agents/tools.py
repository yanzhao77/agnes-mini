"""Tool definitions for agent orchestration."""
from __future__ import annotations
from typing import Any, Dict

from src.models.common import FunctionTool


def get_tool_definitions() -> list[FunctionTool]:
    """Return all tool definitions for the orchestrator."""
    return [
        FunctionTool(
            function={
                "name": "generate_image",
                "description": "Generate an image from a text prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "The image prompt"},
                        "size": {"type": "string", "description": "Image size (e.g. 1024x1024)", "default": None},
                    },
                    "required": ["prompt"],
                },
            }
        ),
        FunctionTool(
            function={
                "name": "generate_video",
                "description": "Generate a video from a text prompt.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "The video prompt"},
                    },
                    "required": ["prompt"],
                },
            }
        ),
        FunctionTool(
            function={
                "name": "chat",
                "description": "Chat with the AI assistant.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "The user message"},
                    },
                    "required": ["message"],
                },
            }
        ),
    ]


TOOL_MAP: Dict[str, str] = {
    "generate_image": "image",
    "generate_video": "video",
    "chat": "chat",
}
