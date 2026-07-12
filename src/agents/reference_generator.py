"""ReferenceGenerator: generate character/scene reference images."""
from __future__ import annotations
import asyncio, httpx
from typing import Any
from src.agents.base import BaseAgent
from src.models.character import Character, CharacterBank, CharacterExpression, CharacterView
from src.models.scene import Scene, SceneBank, SceneVariant

BASE = "https://apihub.agnes-ai.com"
# Headers constructed per-call with actual api_key

async def _img2img(base_url: str, prompt: str, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=120, verify=False) as c:
        for attempt in range(3):
            try:
                r = await c.post(f"{BASE}/v1/images/generations", headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={"model": "agnes-image-2.1-flash", "prompt": prompt + ", same character, same clothing, same lighting", "extra_body": {"image": [base_url]}})
                return r.json()["data"][0]["url"]
            except Exception:
                await asyncio.sleep(2 ** attempt)
    return ""

class ReferenceGenerator(BaseAgent):
    AGENT_TYPE = "reference"
    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
self._api_key = self.settings.api_key if not self.settings.is_mock_mode else "mock"

    async def build_character_bank(self, characters_data: list[dict]) -> CharacterBank:
        bank = CharacterBank()
        for cd in characters_data:
            c = Character(name=cd["name"], base_description=cd.get("appearance_description", ""))
            c.base_image_url = await self._generate_base_image(c.base_description)
            c.views = await self._generate_views(c.base_image_url, c.name)
            c.expressions = await self._generate_expressions(c.base_image_url, c.name)
            bank.characters.append(c)
        return bank

    async def build_scene_bank(self, scenes_data: list[dict]) -> SceneBank:
        bank = SceneBank()
        for sd in scenes_data:
            s = Scene(name=sd["name"], base_description=sd.get("layout_description", ""))
            s.base_image_url = await self._generate_base_image(s.base_description)
            s.variants = await self._generate_variants(s.base_image_url, s.name)
            bank.scenes.append(s)
        return bank

    async def _generate_base_image(self, desc: str) -> str:
        if self._api_key == "mock": return f"https://mock.agnes.ai/images/{hash(desc)}.png"
        async with httpx.AsyncClient(timeout=120, verify=False) as c:
            for attempt in range(3):
                try:
                    r = await c.post(f"{BASE}/v1/images/generations", headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}, json={"model": "agnes-image-2.1-flash", "prompt": desc + ", cinematic, high quality"})
                    return r.json()["data"][0]["url"]
                except: await asyncio.sleep(2**attempt)
        return ""

    async def _generate_views(self, base_url: str, name: str) -> list[CharacterView]:
        views = []
        for vt in ["front", "side", "back", "three_quarter"]:
            url = await _img2img(base_url, f"{name} full body {vt} view", self._api_key) if self._api_key != "mock" else f"https://mock.agnes.ai/{name}_{vt}.png"
            views.append(CharacterView(view_type=vt, image_url=url, prompt=f"{name} {vt} view"))
        return views

    async def _generate_expressions(self, base_url: str, name: str) -> list[CharacterExpression]:
        exps = []
        for exp in ["neutral", "happy", "sad", "surprised", "thoughtful"]:
            url = await _img2img(base_url, f"{name} close-up portrait {exp} expression", self._api_key) if self._api_key != "mock" else f"https://mock.agnes.ai/{name}_{exp}.png"
            exps.append(CharacterExpression(expression=exp, image_url=url, prompt=f"{name} {exp}"))
        return exps

    async def _generate_variants(self, base_url: str, name: str) -> list[SceneVariant]:
        variants = []
        for vt in ["wide_full", "corner_stove", "window_view", "table_close"]:
            url = await _img2img(base_url, f"{name} {vt} angle, same setting", self._api_key) if self._api_key != "mock" else f"https://mock.agnes.ai/{name}_{vt}.png"
            variants.append(SceneVariant(variant_type=vt, image_url=url))
        return variants
