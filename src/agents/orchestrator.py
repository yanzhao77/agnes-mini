"""Orchestrator agent that routes user requests to the appropriate agent."""
from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.agents.image_agent import ImageAgent
from src.agents.text_agent import TextAgent
from src.agents.video_agent import VideoAgent
from src.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an orchestrator agent for the Agnes Mini platform.
Your role is to understand user requests and route them to the appropriate tool.
Available tools: generate_image (create images), generate_video (create videos), chat (text conversation).

For any request that involves generating images or videos, use the appropriate tool.
For general conversation, use the chat tool.
Respond naturally and helpfully."""


class AgentResult:
    """Result from an agent execution."""

    def __init__(
        self,
        text: str = "",
        image_urls: list[str] | None = None,
        video_urls: list[str] | None = None,
        tool_calls: list[dict] | None = None,
    ) -> None:
        self.text = text
        self.image_urls = image_urls or []
        self.video_urls = video_urls or []
        self.tool_calls = tool_calls or []


class OrchestratorAgent(BaseAgent):
    """Orchestrator that routes requests to appropriate sub-agents."""

    AGENT_TYPE = "orchestrator"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self.text_agent = TextAgent(settings)
        self.image_agent = ImageAgent(settings)
        self.video_agent = VideoAgent(settings)

    async def run(self, user_input: str) -> AgentResult:
        """Orchestrate a user request to the appropriate agent(s)."""
        intent = await self._detect_intent(user_input)

        if intent == "image":
            return await self._handle_image(user_input)
        elif intent == "video":
            return await self._handle_video(user_input)
        else:
            return await self._handle_text(user_input)

    async def _detect_intent(self, user_input: str) -> str:
        """Detect user intent based on keywords (no LLM call)."""
        lower = user_input.lower()
        image_keywords = ["generate image", "create image", "make image", "draw", "generate a picture"]
        video_keywords = ["generate video", "create video", "make video", "generate a video"]

        for kw in image_keywords:
            if kw in lower:
                return "image"
        for kw in video_keywords:
            if kw in lower:
                return "video"
        return "text"

    async def _handle_text(self, user_input: str) -> AgentResult:
        response = await self.text_agent.chat(user_input)
        return AgentResult(
            text=response.choices[0].message.content if response.choices else "",
        )

    async def _handle_image(self, user_input: str) -> AgentResult:
        result = await self.image_agent.generate(user_input)
        return AgentResult(
            text=f"Generated {len(result.urls)} image(s).",
            image_urls=result.urls,
        )

    async def _handle_video(self, user_input: str) -> AgentResult:
        result = await self.video_agent.generate(user_input)
        return AgentResult(
            text="Generated video.",
            video_urls=[result.video_url] if result.video_url else [],
        )
