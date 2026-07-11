"""Codex Skill entry point for Agnes Mini."""
from __future__ import annotations

from src.agents.orchestrator import AgentResult, OrchestratorAgent


async def agnes_run(prompt: str) -> AgentResult:
    """Run the Agnes Mini orchestrator with a natural language prompt."""
    orchestrator = OrchestratorAgent()
    return await orchestrator.run(prompt)


def get_available_tools() -> list[str]:
    """Return a list of available tools."""
    return ["chat", "generate_image", "generate_video"]
