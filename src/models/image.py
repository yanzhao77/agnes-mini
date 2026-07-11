"""Data models for image generation with Agnes AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.models.common import AspectRatio, ErrorDetail, ImageSize


class ImageRequest(BaseModel):
    """Request payload for image generation API."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    size: Optional[ImageSize] = None
    aspect_ratio: Optional[AspectRatio] = None
    n: int = 1
    extra_body: Optional[Dict[str, Any]] = None


class ImageData(BaseModel):
    """Image data returned by the API."""

    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None


class ImageResponse(BaseModel):
    """Response from the image generation API."""

    created: int = 0
    data: List[ImageData] = Field(default_factory=list)


class ImageGenerationResult(BaseModel):
    """Result of an image generation operation with metadata."""

    urls: List[str] = Field(default_factory=list)
    local_paths: List[str] = Field(default_factory=list)
    revised_prompt: Optional[str] = None
    model: str = ""
    created: int = 0


class ImageToImageRequest(BaseModel):
    """Request payload for image-to-image generation."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    image: str  # URL or base64 data URI
    strength: Optional[float] = None
    size: Optional[ImageSize] = None
    extra_body: Optional[Dict[str, Any]] = None


class MultiImageCompositionRequest(BaseModel):
    """Request payload for multi-image composition."""

    model: str = "agnes-image-2.1-flash"
    prompt: str
    images: List[str]  # URLs or base64 data URIs
    mode: str = "composition"
    size: Optional[ImageSize] = None
    extra_body: Optional[Dict[str, Any]] = None
