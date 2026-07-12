"""ScriptAnalysisAgent: extract characters, scenes, props from script using LLM."""
from __future__ import annotations
import json, re
from typing import Any
from src.agents.base import BaseAgent
from src.models.character import Character, CharacterBank
from src.models.scene import Scene, SceneBank
from src.models.script import Script, Shot
from src.providers.chat import ChatProvider
from src.providers.mock_chat import MockChatProvider

ANALYSIS_PROMPT = """You are a video script analysis assistant. Analyze this script and output a JSON object with:
- characters: array of {name, appearance_description, clothing_description}
- scenes: array of {name, layout_description, lighting_description}
- shots: array of {shot_number, description, duration, character_refs (list), scene_ref (string), image_prompt, video_prompt}
Output ONLY valid JSON, no markdown wrapping."""

class ScriptAnalysisResult:
    def __init__(self):
        self.characters: list[dict] = []
        self.scenes: list[dict] = []
        self.shots: list[dict] = []

class ScriptAnalysisAgent(BaseAgent):
    AGENT_TYPE = "script_analysis"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._llm = (
            ChatProvider(self.settings) if not self.settings.is_mock_mode
            else MockChatProvider(self.settings)
        )

    async def decompose(self, script_text: str) -> ScriptAnalysisResult:
        prompt = ANALYSIS_PROMPT + "\n\n---\n" + script_text[:8000]
        from src.models.chat import ChatMessage, ChatRequest
        request = ChatRequest(messages=[ChatMessage(role="user", content=prompt)])
        for attempt in range(2):
            raw = ""
            try:
                response = await self._llm.chat(request)
                raw = response.choices[0].message.content or ""
                data = self._parse_json(raw)
                if data:
                    result = ScriptAnalysisResult()
                    result.characters = data.get("characters", [])
                    result.scenes = data.get("scenes", [])
                    result.shots = data.get("shots", [])
                    return result
            except Exception as e:
                self._logger.warning("Attempt %d failed: %s", attempt + 1, e)
                if attempt == 0:
                    prompt += "\n\nPrevious output was not valid JSON. Output ONLY valid JSON."
        raise ValueError(f"Failed after 2 attempts. Raw: {raw[:200]}")

    def _parse_json(self, text: str) -> dict | None:
        text = re.sub(r"^`(?:json)?\s*", "", text.strip())
        text = re.sub(r"\s*`$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return None
