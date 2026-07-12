"""Data models for script decomposition and shot management."""
from __future__ import annotations
from pydantic import BaseModel


class Shot(BaseModel):
    """A single shot/scene in a video script."""
    shot_number: int
    description: str
    scene_type: str = "cinematic"
    camera_angle: str | None = None
    duration: float = 5.0
    sound: str | None = None
    dialog: str | None = None
    image_prompt: str = ""
    video_prompt: str = ""
    reference_image_url: str | None = None
    video_url: str | None = None
    status: str = "pending"


class Script(BaseModel):
    """A complete video script with multiple shots."""
    title: str = "Untitled"
    style: str | None = None
    shots: list[Shot] = []
    total_duration: float = 0

    def model_post_init(self, __context: object) -> None:
        """Auto-calculate total duration."""
        self.total_duration = sum(s.duration for s in self.shots)
