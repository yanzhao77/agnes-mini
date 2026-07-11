"""Real ChatProvider implementation for Agnes AI chat completions API."""
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


class ChatProvider(BaseProvider):
    """Provider for Agnes AI chat completions API."""
    PROVIDER_TYPE = "chat"
    DEFAULT_MODEL = "agnes-2.0-flash"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        payload = self._build_chat_payload(request)
        response = await self._request_with_retry(
            "POST", "/v1/chat/completions", json_data=payload
        )
        return self._parse_chat_response(response.json())

    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatStreamChunk, None]:
        payload = self._build_chat_payload(request)
        payload["stream"] = True
        client = await self._get_client()
        async with client.stream("POST", "/v1/chat/completions", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    chunk = self._parse_stream_chunk(data)
                    if chunk:
                        yield chunk

    async def chat_with_tools(self, request: ChatRequest) -> ChatResponse:
        return await self.chat(request)

    async def chat_with_images(self, request: ChatRequest) -> ChatResponse:
        return await self.chat(request)

    async def chat_with_thinking(self, request: ChatRequest) -> ChatResponse:
        if request.extra_body is None:
            request.extra_body = {}
        request.extra_body["thinking"] = True
        return await self.chat(request)

    def _build_chat_payload(self, request: ChatRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stream:
            payload["stream"] = True
        if request.tools:
            payload["tools"] = [t.model_dump(exclude_none=True) for t in request.tools]
        if request.tool_choice is not None:
            payload["tool_choice"] = request.tool_choice
        if request.extra_body:
            payload.update(request.extra_body)
        return payload

    def _parse_chat_response(self, data: dict[str, Any]) -> ChatResponse:
        choices = []
        for c in data.get("choices", []):
            msg_data = c.get("message", {})
            choices.append(
                ChatChoice(
                    index=c.get("index", 0),
                    message=ChatMessage(**msg_data),
                    finish_reason=FinishReason(c["finish_reason"]) if c.get("finish_reason") else None,
                )
            )
        usage_data = data.get("usage")
        return ChatResponse(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", 0),
            model=data.get("model", self.DEFAULT_MODEL),
            choices=choices,
            usage=Usage(**usage_data) if usage_data else None,
        )

    def _parse_stream_chunk(self, data_str: str) -> ChatStreamChunk | None:
        import json as _json
        try:
            data = _json.loads(data_str)
        except (_json.JSONDecodeError, ValueError):
            return None
        choices_data = data.get("choices", [])
        choices = []
        for c in choices_data:
            delta_data = c.get("delta", {})
            choices.append(
                StreamChoice(
                    index=c.get("index", 0),
                    delta=DeltaMessage(**delta_data),
                    finish_reason=FinishReason(c["finish_reason"]) if c.get("finish_reason") else None,
                )
            )
        return ChatStreamChunk(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", 0),
            model=data.get("model", self.DEFAULT_MODEL),
            choices=choices,
        )
