"""ConsistentGenerator: generate images/videos with character/scene references."""
from __future__ import annotations
import asyncio, httpx
from typing import Any
from src.agents.base import BaseAgent
from src.models.character import CharacterBank
from src.models.scene import SceneBank
from src.models.script import Shot

BASE = "https://apihub.agnes-ai.com"

class ConsistentGenerator(BaseAgent):
    AGENT_TYPE = "consistent"
    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._api_key = settings.api_key
        self.char_bank: CharacterBank | None = None
        self.scene_bank: SceneBank | None = None

    def load_banks(self, char_bank: CharacterBank, scene_bank: SceneBank) -> None:
        self.char_bank = char_bank
        self.scene_bank = scene_bank

    def _pick_char_ref(self, shot: Shot) -> str:
        for c in (self.char_bank.characters if self.char_bank else []):
            for ref in shot.character_refs if hasattr(shot, "character_refs") else []:
                if c.name == ref:
                    if shot.scene_type in ["extreme close-up", "close-up"]:
                        return c.expressions[0].image_url if c.expressions else c.base_image_url
                    return c.views[0].image_url if c.views else c.base_image_url
        return ""

    def _pick_scene_ref(self, shot: Shot) -> str:
        for s in (self.scene_bank.scenes if self.scene_bank else []):
            if s.name == getattr(shot, "scene_ref", ""):
                return s.variants[0].image_url if s.variants else s.base_image_url
        return ""

    async def generate_image(self, shot: Shot) -> str:
        if not self._api_key or self._api_key == "mock":
            return f"https://mock.agnes.ai/shot_{shot.shot_number}.png"
        char_ref = self._pick_char_ref(shot)
        scene_ref = self._pick_scene_ref(shot)
        if not char_ref and not scene_ref:
            return ""
        prompt = shot.video_prompt or shot.image_prompt or shot.description
        refs = [r for r in [char_ref, scene_ref] if r]
        async with httpx.AsyncClient(timeout=120, verify=False) as c:
            h = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
            for attempt in range(3):
                try:
                    body = {"model": "agnes-image-2.1-flash" if len(refs) == 1 else "agnes-image-2.0-flash", "prompt": prompt + ", same character, same setting as reference", "extra_body": {"image": refs}}
                    r = await c.post(f"{BASE}/v1/images/generations", headers=h, json=body)
                    return r.json()["data"][0]["url"]
                except: await asyncio.sleep(2**attempt)
        return ""

    async def generate_video(self, shot: Shot) -> str:
        if not self._api_key or self._api_key == "mock":
            return f"https://mock.agnes.ai/video_{shot.shot_number}.mp4"
        char_ref = self._pick_char_ref(shot)
        if not char_ref: return ""
        prompt = shot.video_prompt or shot.image_prompt or shot.description
        async with httpx.AsyncClient(timeout=30, verify=False) as c:
            h = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
            try:
                r = await c.post(f"{BASE}/v1/videos", headers=h, json={"model": "agnes-video-v2.0", "prompt": prompt, "image": char_ref, "height": 768, "width": 1152, "num_frames": 121, "frame_rate": 24})
                task_id = r.json()["id"]
                for i in range(60):
                    await asyncio.sleep(10)
                    r2 = await c.get(f"{BASE}/agnesapi?video_id={task_id}", headers=h)
                    data = r2.json()
                    if data.get("status") == "completed":
                        return data.get("metadata", {}).get("url", "")
                    if data.get("status") == "failed": return ""
            except: pass
        return ""
