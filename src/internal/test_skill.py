"""agnes-test: Test generation skill."""
from __future__ import annotations


def gen_test_case(class_name: str) -> str:
    return f'"""Tests for {class_name}."""\nfrom __future__ import annotations\nimport pytest\n\n@pytest.mark.asyncio\nasync def test_{class_name.lower()}_basic():\n    assert True\n'


def gen_mock(provider_name: str) -> str:
    return f'"""Mock {provider_name}Provider."""\nfrom __future__ import annotations\nfrom src.providers.base import BaseProvider\n\n\nclass Mock{provider_name}Provider(BaseProvider):\n    PROVIDER_TYPE = "mock_{provider_name.lower()}"\n'


def check_coverage(path: str) -> dict:
    result: dict = {"coverage": 0.0, "missing": [], "pass": False}
    return result
