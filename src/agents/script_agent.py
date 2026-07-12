"""ScriptAgent: decompose scripts into structured shots using LLM."""
from __future__ import annotations
import json
import re
from typing import Any
from src.agents.base import BaseAgent
from src.models.script import Script, Shot
from src.providers.chat import ChatProvider
from src.providers.mock_chat import MockChatProvider

DECOMPOSE_PROMPT = """You are a video script decomposition assistant. Analyze the given script and output a JSON array of shots.
Each shot must have: shot_number(int), description(str), scene_type(str), camera_angle(str|null), duration(float), sound(str|null), image_prompt(str), video_prompt(str).
Output ONLY valid JSON array, no markdown wrapping, no extra text."""


class ScriptAgent(BaseAgent):
    """Agent that decomposes a script text into structured Shot objects."""
    AGENT_TYPE = "script"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._llm: ChatProvider | MockChatProvider = (
            ChatProvider(self.settings) if not self.settings.is_mock_mode
            else MockChatProvider(self.settings)
        )

    async def decompose(self, script_text: str, title: str = "Untitled") -> Script:
        """Parse a script text into a structured Script object using LLM."""
        prompt = DECOMPOSE_PROMPT + "\n\n---\n" + script_text[:8000]
        from src.models.chat import ChatMessage, ChatRequest
        request = ChatRequest(messages=[ChatMessage(role="user", content=prompt)])
        for attempt in range(2):
            raw = ""
            try:
                response = await self._llm.chat(request)
                raw = response.choices[0].message.content or ""
                shots_data = self._parse_json(raw)
                if shots_data:
                    shots = [Shot(**s) for s in shots_data]
                    return Script(title=title, style="cinematic", shots=shots)
            except Exception as e:
                self._logger.warning("Parse attempt %d failed: %s", attempt + 1, e)
                if attempt == 0:
                    prompt += "\n\nYour previous output was not valid JSON. Please output ONLY valid JSON."
        raise ValueError(f"Failed to parse script after 2 attempts. Raw output: {raw[:200]}")

    @staticmethod
    def _parse_json(text: str) -> list[dict] | None:
        """Extract and parse JSON from LLM output, with fallback."""
        text = text.strip()
        text = re.sub(r"^`(?:json)?\s*", "", text)
        text = re.sub(r"\s*`$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
            return None
        except json.JSONDecodeError:
            pass
        match = re.search(r"\[[\s\S]*\]", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None
