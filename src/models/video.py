"""Data models for video generation with Agnes AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.models.common import AspectRatio, VideoDuration, VideoStatus


class VideoRequest(BaseModel):
    """Request payload for video creation API."""

    model: str = "agnes-video-v2.0"
    prompt: str
    duration: Optional[VideoDuration] = None
    size: Optional[str] = None
    aspect_ratio: Optional[AspectRatio] = None
    image_url: Optional[str] = None
    extra_body: Optional[Dict[str, Any]] = None


class VideoTaskResponse(BaseModel):
    """Response from the video creation API."""

    task_id: str = ""
    video_id: Optional[str] = None
    status: VideoStatus = VideoStatus.PENDING
    message: Optional[str] = None


class VideoQueryResponse(BaseModel):
    """Response from the video query API."""

    id: str = ""
    task_id: str = ""
    status: VideoStatus = VideoStatus.PENDING
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    progress: int = 0
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class VideoResult(BaseModel):
    """Final result of a video generation operation."""

    video_url: str = ""
    local_path: Optional[str] = None
    task_id: str = ""
    model: str = ""


class VideoPollConfig(BaseModel):
    """Configuration for video polling behavior."""

    interval: int = Field(default=5, ge=1, description="Poll interval in seconds")
    timeout: int = Field(default=600, ge=30, description="Max polling time in seconds")
    max_retries: int = Field(default=3, ge=0)
