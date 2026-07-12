"""Tests for v2.0 data models."""
from __future__ import annotations
from src.models.character import Character, CharacterBank, CharacterExpression, CharacterView
from src.models.scene import Scene, SceneBank, SceneVariant


def test_character_creation():
    c = Character(name="Grandpa", base_description="70yo Chinese man")
    assert c.name == "Grandpa"
    assert len(c.views) == 0
    assert len(c.expressions) == 0


def test_character_view():
    v = CharacterView(view_type="front", image_url="http://example.com/1.png")
    assert v.view_type == "front"


def test_character_expression():
    e = CharacterExpression(expression="happy", image_url="http://example.com/e.png")
    assert e.expression == "happy"


def test_character_bank():
    c = Character(name="A", base_description="desc")
    bank = CharacterBank(characters=[c])
    assert len(bank.characters) == 1


def test_scene_creation():
    s = Scene(name="Kitchen", base_description="NYE kitchen")
    assert s.name == "Kitchen"


def test_scene_variant():
    v = SceneVariant(variant_type="wide_full", image_url="http://example.com/w.png")
    assert v.variant_type == "wide_full"


def test_scene_bank():
    s = Scene(name="K", base_description="d")
    bank = SceneBank(scenes=[s])
    assert len(bank.scenes) == 1


def test_character_with_views():
    v1 = CharacterView(view_type="front", image_url="1.png")
    v2 = CharacterView(view_type="side", image_url="2.png")
    c = Character(name="G", base_description="d", views=[v1, v2])
    assert len(c.views) == 2
    assert c.views[1].view_type == "side"


def test_character_with_expressions():
    e1 = CharacterExpression(expression="neutral", image_url="n.png")
    e2 = CharacterExpression(expression="happy", image_url="h.png")
    c = Character(name="G", base_description="d", expressions=[e1, e2])
    assert len(c.expressions) == 2


def test_scene_with_variants():
    v = SceneVariant(variant_type="corner_stove")
    s = Scene(name="K", base_description="d", variants=[v])
    assert len(s.variants) == 1


def test_character_serialization():
    c = Character(name="Grandpa", base_description="70yo")
    d = c.model_dump()
    assert d["name"] == "Grandpa"


def test_scene_serialization():
    s = Scene(name="Kitchen", base_description="NYE")
    d = s.model_dump()
    assert d["name"] == "Kitchen"


def test_view_types():
    for vt in ["front", "side", "back", "three_quarter"]:
        v = CharacterView(view_type=vt)
        assert v.view_type == vt


def test_expression_types():
    for e in ["neutral", "happy", "sad", "surprised", "thoughtful"]:
        exp = CharacterExpression(expression=e)
        assert exp.expression == e


def test_variant_types():
    for vt in ["wide_full", "corner_stove", "window_view", "table_close"]:
        v = SceneVariant(variant_type=vt)
        assert v.variant_type == vt
