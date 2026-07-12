"""Scene bank model for maintaining scene consistency."""
from __future__ import annotations
from pydantic import BaseModel


class SceneVariant(BaseModel):
    variant_type: str  # wide_full / corner_stove / window_view / table_close
    image_url: str = ""
    prompt: str = ""


class Scene(BaseModel):
    name: str
    base_description: str = ""
    base_image_url: str = ""
    variants: list[SceneVariant] = []


class SceneBank(BaseModel):
    scenes: list[Scene] = []
