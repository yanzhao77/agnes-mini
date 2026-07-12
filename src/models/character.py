"""Character bank model for maintaining character consistency."""
from __future__ import annotations
from pydantic import BaseModel


class CharacterView(BaseModel):
    view_type: str  # front / side / back / three_quarter
    image_url: str = ""
    prompt: str = ""


class CharacterExpression(BaseModel):
    expression: str  # neutral / happy / sad / surprised / thoughtful
    image_url: str = ""
    prompt: str = ""


class Character(BaseModel):
    name: str
    base_description: str = ""
    base_image_url: str = ""
    views: list[CharacterView] = []
    expressions: list[CharacterExpression] = []


class CharacterBank(BaseModel):
    characters: list[Character] = []
