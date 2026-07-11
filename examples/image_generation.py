"""Image generation example."""
from __future__ import annotations
from src.agents.image_agent import ImageAgent


async def main():
    agent = ImageAgent()
    result = await agent.generate("A beautiful sunset over mountains")
    print(f"Generated {len(result.urls)} image(s):", result.urls)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
