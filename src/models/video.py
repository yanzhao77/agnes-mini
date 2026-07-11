"""Data models for video generation with Agnes AI."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.models.common import AspectRatio, VideoDuration, VideoStatus


class VideoRequest(BaseModel):
    """Request payload for video creation API."""

    model: str = "agnes-video-v2.0"
    prompt: str
    duration: VideoDuration | None = None
    size: str | None = None
    aspect_ratio: AspectRatio | None = None
    image_url: str | None = None
    extra_body: dict[str, Any] | None = None


class VideoTaskResponse(BaseModel):
    """Response from the video creation API."""

    task_id: str = ""
    video_id: str | None = None
    status: VideoStatus = VideoStatus.PENDING
    message: str | None = None


class VideoQueryResponse(BaseModel):
    """Response from the video query API."""

    id: str = ""
    task_id: str = ""
    status: VideoStatus = VideoStatus.PENDING
    video_url: str | None = None
    video_id: str | None = None
    progress: int = 0
    error: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class VideoResult(BaseModel):
    """Final result of a video generation operation."""

    video_url: str = ""
    local_path: str | None = None
    task_id: str = ""
    model: str = ""


class VideoPollConfig(BaseModel):
    """Configuration for video polling behavior."""

    interval: int = Field(default=5, ge=1, description="Poll interval in seconds")
    timeout: int = Field(default=600, ge=30, description="Max polling time in seconds")
    max_retries: int = Field(default=3, ge=0)
