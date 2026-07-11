"""Data models for image generation with Agnes AI."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.models.common import AspectRatio, ImageSize


class ImageRequest(BaseModel):
    """Request payload for image generation API."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    size: ImageSize | None = None
    aspect_ratio: AspectRatio | None = None
    n: int = 1
    extra_body: dict[str, Any] | None = None


class ImageData(BaseModel):
    """Image data returned by the API."""

    url: str | None = None
    b64_json: str | None = None
    revised_prompt: str | None = None


class ImageResponse(BaseModel):
    """Response from the image generation API."""

    created: int = 0
    data: list[ImageData] = Field(default_factory=list)


class ImageGenerationResult(BaseModel):
    """Result of an image generation operation with metadata."""

    urls: list[str] = Field(default_factory=list)
    local_paths: list[str] = Field(default_factory=list)
    revised_prompt: str | None = None
    model: str = ""
    created: int = 0


class ImageToImageRequest(BaseModel):
    """Request payload for image-to-image generation."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    image: str  # URL or base64 data URI
    strength: float | None = None
    size: ImageSize | None = None
    extra_body: dict[str, Any] | None = None


class MultiImageCompositionRequest(BaseModel):
    """Request payload for multi-image composition."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    images: list[str]  # URLs or base64 data URIs
    mode: str = "composition"
    size: ImageSize | None = None
    extra_body: dict[str, Any] | None = None
