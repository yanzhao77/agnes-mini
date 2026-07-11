"""Chat demo - simple conversation with the AI."""
from __future__ import annotations
from src.agents.text_agent import TextAgent


async def main():
    agent = TextAgent()
    response = await agent.chat("Hello! What can you do?")
    print(f"AI: {response.choices[0].message.content}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
