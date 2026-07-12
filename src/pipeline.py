"""Pipeline orchestrator."""
from __future__ import annotations
import asyncio, json, os, time
from typing import Any
from src.agents.script_agent import ScriptAgent
from src.agents.image_agent import ImageAgent
from src.agents.video_agent import VideoAgent
from src.models.script import Script, Shot
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)

class VideoRateLimiter:
    def __init__(self, rpm: int = 1) -> None:
        self.interval = 60.0 / max(rpm, 1)
        self._last: float = 0.0
    async def acquire(self) -> None:
        now = time.time()
        wait = self.interval - (now - self._last)
        if wait > 0:
            logger.info("Rate limiter: waiting %.1fs", wait)
            await asyncio.sleep(wait)
        self._last = time.time()

class PipelineResult:
    def __init__(self) -> None:
        self.shots: list[Shot] = []
        self.errors: list[str] = []
        self.state_path: str = ""

class Pipeline:
    def __init__(self, settings: Any = None) -> None:
        self.settings = settings or get_settings()
        self.script_agent = ScriptAgent(self.settings)
        self.image_agent = ImageAgent(self.settings)
        self.video_agent = VideoAgent(self.settings)
        self.rate_limiter = VideoRateLimiter(rpm=getattr(self.settings, "video_rpm", 1))
        self._state: dict = {}

    async def run(self, script_text: str, title: str = "Script") -> PipelineResult:
        result = PipelineResult()
        out_dir = self.settings.output_dir
        os.makedirs(out_dir, exist_ok=True)
        self._state = {"title": title, "shots": [], "errors": [], "status": "running"}

        logger.info("Step 1: Decomposing script...")
        try:
            script = await self.script_agent.decompose(script_text, title)
        except Exception as e:
            result.errors.append(f"Script decompose failed: {e}")
            self._state["status"] = "failed"
            self._save_state(out_dir)
            return result

        result.shots = script.shots

        logger.info("Step 2: Generating images...")
        for shot in script.shots:
            if not shot.image_prompt:
                result.errors.append(f"Shot {shot.shot_number}: no image_prompt")
                continue
            try:
                img = await self.image_agent.generate(shot.image_prompt)
                if img.urls:
                    shot.reference_image_url = img.urls[0]
                    shot.status = "completed"
                else: shot.status = "failed"
            except Exception as e:
                result.errors.append(f"Shot {shot.shot_number} image: {e}")
                shot.status = "failed"
            self._save_state(out_dir)

        logger.info("Step 3: Generating videos...")
        for shot in script.shots:
            if shot.status == "failed": continue
            await self.rate_limiter.acquire()
            try:
                vid = await self.video_agent.generate(shot.video_prompt or shot.image_prompt)
                shot.video_url = vid.video_url
                shot.status = "completed"
            except Exception as e:
                result.errors.append(f"Shot {shot.shot_number} video: {e}")
                shot.status = "failed"
            self._save_state(out_dir)

        self._state["status"] = "completed"
        self._save_state(out_dir)
        result.state_path = os.path.join(out_dir, "pipeline_state.json")
        return result

    def _save_state(self, out_dir: str) -> None:
        sp = os.path.join(out_dir, "pipeline_state.json")
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)
