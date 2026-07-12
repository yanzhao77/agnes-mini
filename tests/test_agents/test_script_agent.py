"""Tests for ScriptAgent."""
from __future__ import annotations
import json, pytest
from src.agents.script_agent import ScriptAgent

def test_parse_json_clean():
    data = json.dumps([{"shot_number": 1, "description": "Test"}])
    result = ScriptAgent._parse_json(data)
    assert result is not None
    assert result[0]["shot_number"] == 1

def test_parse_json_invalid():
    assert ScriptAgent._parse_json("not json") is None

def test_parse_json_empty():
    assert ScriptAgent._parse_json("") is None
