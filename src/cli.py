"""CLI commands for Agnes Mini."""
from __future__ import annotations
import asyncio
from typing import Optional
import typer
from src.agents.orchestrator import OrchestratorAgent
from src.agents.text_agent import TextAgent
from src.agents.image_agent import ImageAgent
from src.agents.video_agent import VideoAgent

app = typer.Typer(name="agnes", help="Agnes Mini SDK")


@app.command()
def chat(
    message: str = typer.Argument(..., help="Your message"),
    system: Optional[str] = typer.Option(None, "--system", "-s"),
):
    async def _run():
        agent = TextAgent()
        response = await agent.chat(message, system)
        if response.choices:
            typer.echo(response.choices[0].message.content)
    asyncio.run(_run())


@app.command()
def image(
    prompt: str = typer.Argument(..., help="Image prompt"),
    output: Optional[str] = typer.Option(None, "--output", "-o"),
):
    async def _run():
        agent = ImageAgent()
        result = await agent.generate_and_save(prompt, output)
        for url in result.urls:
            typer.echo(f"Image: {url}")
    asyncio.run(_run())


@app.command()
def video(
    prompt: str = typer.Argument(..., help="Video prompt"),
):
    async def _run():
        agent = VideoAgent()
        result = await agent.generate(prompt)
        typer.echo(f"Video URL: {result.video_url}")
    asyncio.run(_run())


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Prompt for orchestrator"),
):
    async def _run():
        orch = OrchestratorAgent()
        result = await orch.run(prompt)
        if result.text:
            typer.echo(result.text)
    asyncio.run(_run())
