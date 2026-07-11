"""Mock video provider for development and testing without a real API key."""

from __future__ import annotations

from typing import Any, Optional
import asyncio

from src.exceptions import VideoPollingError, VideoTimeoutError
from src.models.common import VideoStatus
from src.models.video import (
    VideoPollConfig,
    VideoQueryResponse,
    VideoRequest,
    VideoResult,
    VideoTaskResponse,
)
from src.providers.base import BaseProvider


class MockVideoProvider(BaseProvider):
    """Mock video provider that simulates the complete video lifecycle."""

    PROVIDER_TYPE = "mock_video"
    DEFAULT_MODEL = "agnes-video-v2.0"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._tasks: dict[str, Any] = {}
        self._task_counter: int = 0

    async def create_task(self, request: VideoRequest) -> VideoTaskResponse:
        """Create a mock video task."""
        self._task_counter += 1
        task_id = f"mock-video-task-{self._task_counter}"
        video_id = f"mock-video-{self._task_counter}"
        self._tasks[task_id] = {
            "video_id": video_id,
            "status": VideoStatus.PENDING,
            "progress": 0,
            "prompt": request.prompt,
        }
        return VideoTaskResponse(
            task_id=task_id,
            video_id=video_id,
            status=VideoStatus.PENDING,
        )

    async def query_task(self, task_id: str) -> VideoQueryResponse:
        """Query the status of a mock video task."""
        task = self._tasks.get(task_id)
        if not task:
            return VideoQueryResponse(
                id="unknown",
                task_id=task_id,
                status=VideoStatus.FAILED,
                error="Task not found",
            )

        if task["status"] == VideoStatus.PENDING:
            task["status"] = VideoStatus.PROCESSING
            task["progress"] = 10
        elif task["status"] == VideoStatus.PROCESSING:
            if task["progress"] >= 100:
                task["status"] = VideoStatus.COMPLETED
            else:
                task["progress"] += 30
        elif task["status"] == VideoStatus.COMPLETED:
            pass

        return VideoQueryResponse(
            id=task_id,
            task_id=task_id,
            status=task["status"],
            video_url=(
                f"https://mock.agnes.ai/videos/{task['video_id']}.mp4"
                if task["status"] == VideoStatus.COMPLETED
                else None
            ),
            video_id=task.get("video_id"),
            progress=task["progress"],
        )

    async def poll_task(
        self,
        task_id: str,
        config: VideoPollConfig | None = None,
    ) -> VideoResult:
        """Poll a mock video task until completion or timeout."""
        poll_config = config or VideoPollConfig()
        elapsed = 0

        while elapsed < poll_config.timeout:
            result = await self.query_task(task_id)

            if result.status == VideoStatus.COMPLETED and result.video_url:
                return VideoResult(
                    video_url=result.video_url,
                    task_id=task_id,
                    model=self.DEFAULT_MODEL,
                )

            if result.status == VideoStatus.FAILED:
                raise VideoPollingError(
                    result.error or f"Video task {task_id} failed"
                )

            await asyncio.sleep(poll_config.interval)
            elapsed += poll_config.interval

        raise VideoTimeoutError(
            f"Video task {task_id} did not complete within {poll_config.timeout}s"
        )

    async def download_video(self, url: str, output_path: str) -> str:
        """Mock download - just return the output path."""
        return output_path
