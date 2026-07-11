# Agnes Mini

Lightweight Python SDK for Agnes AI API.

## Features

- Chat completions (agnes-2.0-flash)
- Image generation (agnes-image-2.1-flash)
- Video generation (agnes-video-v2.0)
- Mock mode (no API key needed)
- Type-safe models (Pydantic v2)
- Async HTTP (httpx)
- CLI interface
- Agent orchestration

## Quick Start

`python
from src.agents.text_agent import TextAgent
import asyncio

async def main():
    agent = TextAgent()
    response = await agent.chat("Hello!")
    print(response.choices[0].message.content)

asyncio.run(main())
`

## License MIT
