"""Abstract base class for all agents."""
from __future__ import annotations
from abc import ABC
from typing import Any, ClassVar
from src.config import Settings, get_settings
from src.logger import get_logger


class BaseAgent(ABC):
    """Abstract base class providing common agent functionality."""
    AGENT_TYPE: ClassVar[str] = "base"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._logger = get_logger(f"agnes.agent.{self.AGENT_TYPE}")
