"""ConsistentPipeline v2: script -> character/scene banks -> consistent generation."""
from __future__ import annotations
import asyncio, json, os, time
from typing import Any
from src.agents.script_analysis_agent import ScriptAnalysisAgent
from src.agents.reference_generator import ReferenceGenerator
from src.agents.consistent_generator import ConsistentGenerator
from src.models.character import CharacterBank, Character
from src.models.scene import SceneBank, Scene
from src.models.script import Script, Shot
from src.config import get_settings
from src.logger import get_logger
logger = get_logger(__name__)

class VideoRateLimiter:
    def __init__(self, rpm: int = 1):
        self.interval = 60.0 / max(rpm, 1)
        self._last: float = 0.0
    async def acquire(self):
        now = time.time()
        w = self.interval - (now - self._last)
        if w > 0: await asyncio.sleep(w)
        self._last = time.time()

class ConsistentPipeline:
    def __init__(self, settings: Any = None):
        self.settings = settings or get_settings()
        self.analysis_agent = ScriptAnalysisAgent(self.settings)
        self.ref_generator = ReferenceGenerator(self.settings)
        self.rate_limiter = VideoRateLimiter(rpm=1)
        self._state: dict = {}

    async def run(self, script_text: str) -> dict:
        out = self.settings.output_dir
        os.makedirs(out, exist_ok=True)
        self._state = {"status": "running", "steps": []}
        self._save_state(out)
        logger.info("Step 1: Analyzing script...")
        analysis = await self.analysis_agent.decompose(script_text)
        self._state["steps"].append({"name": "analysis", "shots": len(analysis.shots)})
        self._save_state(out)
        logger.info("Step 2: Building reference banks...")
        char_bank = await self.ref_generator.build_character_bank(analysis.characters)
        scene_bank = await self.ref_generator.build_scene_bank(analysis.scenes)
        self._state["steps"].append({"name": "references", "chars": len(char_bank.characters), "scenes": len(scene_bank.scenes)})
        self._save_state(out)
        logger.info("Step 3: Generating consistent shots...")
        con = ConsistentGenerator(self.settings)
        con.load_banks(char_bank, scene_bank)
        shot_results = []
        for sd in analysis.shots:
            s = Shot(shot_number=sd["shot_number"], description=sd.get("description",""), duration=sd.get("duration",5.0))
            if hasattr(s, "character_refs"): s.character_refs = sd.get("character_refs",[])
            if hasattr(s, "scene_ref"): s.scene_ref = sd.get("scene_ref","")
            s.image_prompt = sd.get("image_prompt","")
            s.video_prompt = sd.get("video_prompt","")
            logger.info("  Generating image for shot %d...", s.shot_number)
            img_url = await con.generate_image(s)
            logger.info("  Generating video for shot %d...", s.shot_number)
            if not self.settings.is_mock_mode:
                await self.rate_limiter.acquire()
            else:
                await asyncio.sleep(0.1)
            vid_url = await con.generate_video(s)
            shot_results.append({"shot": s.shot_number, "image": img_url or "", "video": vid_url or ""})
            self._state["last_shot"] = s.shot_number
            self._save_state(out)
        self._state["status"] = "completed"
        self._state["results"] = shot_results
        self._save_state(out)
        logger.info("Pipeline complete! %d shots generated.", len(shot_results))
        return self._state

    def _save_state(self, out: str):
        with open(os.path.join(out, "pipeline_v2_state.json"), "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)
