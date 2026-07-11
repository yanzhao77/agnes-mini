"""Video agent wrapping VideoProvider with polling lifecycle."""
from __future__ import annotations
from typing import Any
from src.agents.base import BaseAgent
from src.models.video import VideoPollConfig, VideoRequest, VideoResult
from src.providers.video import VideoProvider
from src.providers.mock_video import MockVideoProvider


class VideoAgent(BaseAgent):
    """Agent for video generation."""
    AGENT_TYPE = "video"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._provider: VideoProvider | MockVideoProvider = (
            VideoProvider(self.settings) if not self.settings.is_mock_mode
            else MockVideoProvider(self.settings)
        )

    async def generate(self, prompt: str) -> VideoResult:
        request = VideoRequest(model=self.settings.video_model, prompt=prompt)
        created = await self._provider.create_task(request)
        config = VideoPollConfig(
            interval=self.settings.video_poll_interval,
            timeout=self.settings.video_poll_timeout,
        )
        return await self._provider.poll_task(created.task_id, config)

    async def create_and_wait(self, request: VideoRequest) -> VideoResult:
        created = await self._provider.create_task(request)
        config = VideoPollConfig(
            interval=self.settings.video_poll_interval,
            timeout=self.settings.video_poll_timeout,
        )
        return await self._provider.poll_task(created.task_id, config)
