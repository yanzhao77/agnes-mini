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

ANALYSIS_PROMPT = """You are a video script analysis assistant. Analyze this script and output ONLY valid JSON (no markdown). Use EXACT key names:
characters=[{name,appearance_description,clothing_description}]
scenes=[{name,layout_description,lighting_description}]
shots=[{shot_number,description,duration(5.0 as float),character_refs(list of character names),scene_ref(string),image_prompt, video_prompt}].
IMPORTANT: Use EXACT key names: appearance_description, clothing_description, layout_description, lighting_description, shot_number."""

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
        if self.settings.is_mock_mode:
            result = ScriptAnalysisResult()
            result.characters = [{"name": "Grandpa", "appearance_description": "Old man in Mao suit"}, {"name": "Girl", "appearance_description": "Android girl in linen"}]
            result.scenes = [{"name": "Kitchen", "layout_description": "NYE kitchen"}]
            result.shots = [{"shot_number": i, "description": f"Shot {i}", "duration": 5.0, "character_refs": ["Grandpa"], "scene_ref": "Kitchen"} for i in range(1, 10)]
            return result
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
                    result.characters = self._normalize_keys(data.get("characters", []), {"appearance":"appearance_description","clothing":"clothing_description","layout":"layout_description","lighting":"lighting_description"})
                    result.scenes = self._normalize_keys(data.get("scenes", []), {"layout":"layout_description","lighting":"lighting_description"})
                    result.shots = self._normalize_keys(data.get("shots", []), {"id":"shot_number","time":"description"})
                    return result
            except Exception as e:
                self._logger.warning("Attempt %d failed: %s", attempt + 1, e)
                if attempt == 0:
                    prompt += "\n\nPrevious output was not valid JSON. Output ONLY valid JSON."
        raise ValueError(f"Failed after 2 attempts. Raw: {raw[:200]}")

    @staticmethod
    def _normalize_keys(data: list[dict], mapping: dict) -> list[dict]:
        """Normalize keys in a list of dicts using the provided mapping."""
        result = []
        for item in data:
            new_item = {}
            for k, v in item.items():
                new_item[mapping.get(k, k)] = v
            result.append(new_item)
        return result

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
