"""agnes-review: Code review skill."""
from __future__ import annotations

import os


def check_architecture(path: str) -> dict:
    result: dict = {"errors": [], "warnings": [], "pass": True}
    if not os.path.exists(path):
        result["errors"].append("Path does not exist")
        result["pass"] = False
    return result
