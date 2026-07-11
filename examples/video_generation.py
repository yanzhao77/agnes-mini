"""Video generation example."""
from __future__ import annotations
from src.agents.video_agent import VideoAgent


async def main():
    agent = VideoAgent()
    result = await agent.generate("A drone flying over a city")
    print(f"Video URL: {result.video_url}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
