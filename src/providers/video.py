"""Real VideoProvider for Agnes AI video generation API."""
from __future__ import annotations

import asyncio
from typing import Any

from src.exceptions import VideoCreationError, VideoPollingError, VideoTimeoutError
from src.models.common import VideoStatus
from src.models.video import (
    VideoPollConfig,
    VideoQueryResponse,
    VideoRequest,
    VideoResult,
    VideoTaskResponse,
)
from src.providers.base import BaseProvider


class VideoProvider(BaseProvider):
    """Provider for Agnes AI video generation API."""
    PROVIDER_TYPE = "video"
    DEFAULT_MODEL = "agnes-video-v2.0"

    async def create_task(self, request: VideoRequest) -> VideoTaskResponse:
        payload: dict[str, Any] = {"model": request.model, "prompt": request.prompt}
        if request.duration:
            payload["duration"] = request.duration.value
        if request.size:
            payload["size"] = request.size
        if request.aspect_ratio:
            payload["aspect_ratio"] = request.aspect_ratio.value
        if request.image_url:
            payload["image_url"] = request.image_url
        if request.extra_body:
            payload.update(request.extra_body)
        try:
            response = await self._request_with_retry("POST", "/v1/videos", json_data=payload)
        except Exception as e:
            raise VideoCreationError(f"Video task creation failed: {e}") from e
        data = response.json()
        return VideoTaskResponse(
            task_id=data.get("task_id", data.get("id", "")),
            video_id=data.get("video_id"),
            status=VideoStatus(data.get("status", "pending")),
            message=data.get("message"),
        )

    async def query_task(self, task_id: str) -> VideoQueryResponse:
        try:
            response = await self._request_with_retry("GET", f"/v1/videos/{task_id}")
        except Exception:
            response = await self._request_with_retry("GET", f"/agnesapi?video_id={task_id}")
        data = response.json()
        return VideoQueryResponse(
            id=data.get("id", task_id),
            task_id=data.get("task_id", task_id),
            status=VideoStatus(data.get("status", "pending")),
            video_url=data.get("video_url"),
            video_id=data.get("video_id"),
            progress=data.get("progress", 0),
            error=data.get("error"),
        )

    async def poll_task(self, task_id: str, config: VideoPollConfig | None = None) -> VideoResult:
        poll_config = config or VideoPollConfig()
        elapsed = 0
        while elapsed < poll_config.timeout:
            result = await self.query_task(task_id)
            if result.status == VideoStatus.COMPLETED and result.video_url:
                return VideoResult(video_url=result.video_url, task_id=task_id, model=self.DEFAULT_MODEL)
            if result.status == VideoStatus.FAILED:
                raise VideoPollingError(result.error or f"Video task {task_id} failed")
            await asyncio.sleep(poll_config.interval)
            elapsed += poll_config.interval
        raise VideoTimeoutError(f"Video task {task_id} did not complete within {poll_config.timeout}s")

    async def download_video(self, url: str, output_path: str) -> str:
        client = await self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
