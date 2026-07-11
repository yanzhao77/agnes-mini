"""Multi-modal agent example using the orchestrator."""
from __future__ import annotations
from src.agents.orchestrator import OrchestratorAgent


async def main():
    orch = OrchestratorAgent()
    for prompt in ["Hello", "generate image of a cyberpunk city", "generate video of a drone"]:
        print(f"\nPrompt: {prompt}")
        result = await orch.run(prompt)
        if result.text:
            print(f"  {result.text[:100]}")
        if result.image_urls:
            print(f"  Images: {result.image_urls}")
        if result.video_urls:
            print(f"  Videos: {result.video_urls}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
