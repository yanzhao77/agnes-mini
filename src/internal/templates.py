"""Code templates for code generation tools."""
PROVIDER_TEMPLATE = """\"\"\"Real {name}Provider for Agnes AI {desc} API.\"\"\"
from __future__ import annotations
from typing import Any, Dict
from src.providers.base import BaseProvider
class {name}Provider(BaseProvider):
    PROVIDER_TYPE = "{lname}"
    DEFAULT_MODEL = "{model}"
"""
MOCK_PROVIDER_TEMPLATE = """\"\"\"Mock {name}Provider.\"\"\"
from __future__ import annotations
from src.providers.base import BaseProvider
class Mock{name}Provider(BaseProvider):
    PROVIDER_TYPE = "mock_{lname}"
"""
AGENT_TEMPLATE = """\"\"\"{name}Agent wrapping {name}Provider.\"\"\"
from __future__ import annotations
from src.agents.base import BaseAgent
class {name}Agent(BaseAgent):
    AGENT_TYPE = "{lname}"
"""
