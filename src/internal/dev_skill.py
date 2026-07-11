"""agnes-dev: Development tool skill for code generation."""
from __future__ import annotations

import re

from src.internal.templates import AGENT_TEMPLATE, PROVIDER_TEMPLATE


def gen_provider(name: str, model: str = "agnes-model-v1", desc: str = "") -> str:
    lname = name.lower().replace(" ", "_")
    d = desc or name
    return PROVIDER_TEMPLATE.format(name=name, lname=lname, model=model, desc=d)


def gen_agent(name: str, desc: str = "") -> str:
    lname = name.lower().replace(" ", "_")
    d = desc or name
    return AGENT_TEMPLATE.format(name=name, lname=lname, desc=d)


def gen_test_stub(class_name: str) -> str:
    return f'"""Tests for {class_name}."""\nfrom __future__ import annotations\nimport pytest\n\n@pytest.mark.asyncio\nasync def test_{class_name.lower()}_basic():\n    assert True\n'


def analyze_error(error_str: str) -> dict:
    result: dict = {"type": "unknown", "message": error_str, "line": None, "file": None}
    line_match = re.search(r'line (\d+)', error_str)
    if line_match:
        result["line"] = int(line_match.group(1))
    file_match = re.search(r'File "([^"]+)"', error_str)
    if file_match:
        result["file"] = file_match.group(1)
    if "ModuleNotFoundError" in error_str:
        result["type"] = "missing_import"
    elif "SyntaxError" in error_str:
        result["type"] = "syntax_error"
    return result
