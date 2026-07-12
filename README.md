<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/version-2.0.0-blueviolet" alt="Version 2.0.0">
  <img src="https://img.shields.io/badge/coverage-65%25-brightgreen" alt="Coverage 65%+">
  <img src="https://img.shields.io/badge/code%20style-ruff-000000" alt="Ruff">
</p>

<p align="center">
  <strong>Lightweight Python SDK for the Agnes AI API</strong>
  <br>
  Chat, images, videos, and script-to-video pipelines — all with type safety and async support.
</p>

---

## Features

- **Chat Completions** — streaming, tools, multi-modal, thinking mode
- **Image Generation** — text-to-image, image-to-image, multi-image composition
- **Video Generation** — async task creation with polling and auto-download
- **Smart Orchestration** — agents route requests to the right provider automatically
- **Script-to-Video Pipeline** — decompose scripts, generate consistent character/scene banks, produce videos
- **Mock Mode** — develop and test without an API key (zero configuration needed)
- **Type-Safe** — Pydantic v2 models throughout
- **Async Native** — built on httpx with automatic retry and rate limiting
- **CLI Interface** — Typer-based command-line tool
- **Graceful Error Handling** — rich exception hierarchy with descriptive messages

---

## Installation

### From source

```bash
git clone https://github.com/yourusername/agnes-mini.git
cd agnes-mini

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS/Linux

# Install in editable mode
pip install -e .
```

### With CLI extras

```bash
pip install -e ".[cli]"
```

### With development tools

```bash
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Set up your API key (or skip for mock mode)

```bash
cp .env.example .env
```

Edit .env:

```ini
AGNES_API_KEY=sk-your-key-here
AGNES_BASE_URL=https://api.agnesai.com
```

### 2. Chat with the AI

```python
import asyncio
from src.agents.text_agent import TextAgent

async def main():
    agent = TextAgent()
    response = await agent.chat("Hello! What can you do?")
    print(response.choices[0].message.content)

asyncio.run(main())
```

### 3. Generate an image

```python
import asyncio
from src.agents.image_agent import ImageAgent

async def main():
    agent = ImageAgent()
    result = await agent.generate("A cyberpunk city at night, neon lights")
    for url in result.urls:
        print(url)

asyncio.run(main())
```

### 4. Use the CLI

```bash
agnes chat "Tell me about Agnes AI"
agnes image "A beautiful sunset over mountains"
agnes video "A drone flying over a futuristic city"
agnes run "Generate an image of a cat wearing a hat"
```

> No API key? No problem — all examples work in **mock mode** with zero configuration.

---

## Configuration

All settings are loaded from environment variables or a .env file:

| Variable | Default | Description |
|----------|---------|-------------|
| AGNES_API_KEY | "" | API key (empty = mock mode) |
| AGNES_BASE_URL | https://api.agnesai.com | API base URL |
| AGNES_CHAT_MODEL | agnes-2.0-flash | Chat model name |
| AGNES_IMAGE_MODEL | agnes-image-2.1-flash | Image model name |
| AGNES_VIDEO_MODEL | agnes-video-v2.0 | Video model name |
| AGNES_TIMEOUT | 60 | HTTP request timeout (seconds) |
| AGNES_MAX_RETRIES | 3 | Max retries for failed requests |
| AGNES_VIDEO_POLL_INTERVAL | 5 | Video status poll interval (seconds) |
| AGNES_VIDEO_POLL_TIMEOUT | 600 | Max video generation wait (seconds) |
| AGNES_LOG_LEVEL | INFO | Logging level |
| AGNES_OUTPUT_DIR | ./output | Output directory for generated files |

---

## Python API

### Chat

```python
from src.models.chat import ChatRequest, ChatMessage
from src.providers.chat import ChatProvider

async def example():
    provider = ChatProvider()
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Hello!")],
        temperature=0.7,
        max_tokens=1024,
    )
    response = await provider.chat(request)
    print(response.choices[0].message.content)
```

**Streaming:**

```python
async for chunk in provider.chat_stream(request):
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Thinking mode:**

```python
request = ChatRequest(
    messages=[ChatMessage(role="user", content="Explain quantum computing")],
    extra_body={"thinking": True},
)
```

### Image Generation

```python
from src.models.image import ImageRequest, ImageSize
from src.providers.image import ImageProvider

async def example():
    provider = ImageProvider()
    request = ImageRequest(
        prompt="A serene Japanese garden in autumn",
        n=1,
        size=ImageSize.SIZE_1024x1024,
    )
    response = await provider.text_to_image(request)
    for img in response.data:
        print(f"URL: {img.url}")
```

**Image-to-Image:**

```python
from src.models.image import ImageToImageRequest
request = ImageToImageRequest(
    prompt="Make it a winter scene with snow",
    image="https://example.com/summer_garden.jpg",
    strength=0.7,
)
response = await provider.image_to_image(request)
```

**Multi-Image Composition:**

```python
from src.models.image import MultiImageCompositionRequest
request = MultiImageCompositionRequest(
    prompt="Combine these images into one coherent scene",
    images=["https://example.com/bg.jpg", "https://example.com/character.png"],
    mode="composition",
)
response = await provider.multi_image_composition(request)
```

### Video Generation

```python
from src.models.video import VideoRequest, VideoDuration
from src.providers.video import VideoProvider

async def example():
    provider = VideoProvider()
    request = VideoRequest(
        prompt="Cinematic drone shot over a cyberpunk city at night",
        duration=VideoDuration.SECONDS_5,
    )

    # Step 1: Create the video task
    task = await provider.create_task(request)
    print(f"Task ID: {task.task_id}")

    # Step 2: Poll until complete
    result = await provider.poll_task(task.task_id)
    print(f"Video URL: {result.video_url}")

    # Step 3: Download the video
    local_path = await provider.download_video(result.video_url, "./output/video.mp4")
```

---

## Agent Orchestration

The OrchestratorAgent intelligently routes requests to the right sub-agent based on intent detection:

```python
from src.agents.orchestrator import OrchestratorAgent

async def demo():
    orch = OrchestratorAgent()

    # Automatically routed to TextAgent
    result = await orch.run("What is the capital of France?")
    print(result.text)

    # Automatically routed to ImageAgent
    result = await orch.run("Generate an image of a peaceful mountain lake")
    print(result.image_urls)

    # Automatically routed to VideoAgent
    result = await orch.run("Create a video of waves crashing on a beach")
    print(result.video_urls)
```

---

## Script-to-Video Pipeline (v2)

The ConsistentPipeline takes a narrative script and produces a complete video with consistent characters and scenes:

```python
import asyncio
from src.pipeline_v2 import ConsistentPipeline

async def main():
    pipeline = ConsistentPipeline()

    script = \"\"\"
    Title: The Last Dumpling
    An old man in a Mao suit prepares dumplings on New Year's Eve.
    His android granddaughter watches quietly...
    \"\"\"

    result = await pipeline.run(script)
    print(f"Status: {result['status']}")
    for shot in result.get("results", []):
        print(f"  Shot {shot['shot']}: image={shot['image']}, video={shot['video']}")

asyncio.run(main())
```

**What it does:**

1. **Script Analysis** — LLM decomposes the script into characters, scenes, and shots
2. **Reference Generation** — builds character banks (multi-view, expressions) and scene banks (variants)
3. **Consistent Generation** — produces images and videos using character/scene references for visual consistency
4. **Rate Limiting** — respects API rate limits during video generation
5. **State Persistence** — saves pipeline state after every step for resumability

---

## Mock Mode

When AGNES_API_KEY is empty (or set to "mock"), all providers automatically fall back to mock implementations:

- **MockChatProvider** — responds with natural placeholder answers
- **MockImageProvider** — returns placeholder URLs (no real generation cost)
- **MockVideoProvider** — simulates task creation and polling
- **Mock Script Analysis** — returns predefined character/scene/shot structures

This allows full development, testing, and CI integration without API credentials.

---

## Error Handling

Agnes Mini provides a rich exception hierarchy:

| Exception | When It Occurs |
|-----------|----------------|
| ProviderAuthenticationError | Invalid API key (401) |
| ProviderRateLimitError | Rate limit exceeded (429) |
| ProviderServerError | Server-side error (5xx) |
| ProviderTimeoutError | Request timed out |
| VideoCreationError | Video task creation failed |
| VideoTimeoutError | Video generation exceeded timeout |
| ConfigError | Configuration issues |
| AgentExecutionError | Agent execution failed |

All exceptions inherit from AgnesMiniError for clean catch-all handling:

```python
from src.exceptions import AgnesMiniError, ProviderAuthenticationError

try:
    result = await agent.generate(prompt)
except ProviderAuthenticationError:
    print("Please check your API key")
except AgnesMiniError as e:
    print(f"Agnes Mini error: {e}")
```

---

## Architecture

```
???????????????????????????????????????????????
?                   CLI                        ?
?           (typer — src/cli.py)               ?
???????????????????????????????????????????????
?                  Agents                      ?
?  ???????? ???????? ???????? ?????????????? ?
?  ?Text  — ?Image — ?Video — ?Orchestrator — ?
?  ?Agent — ?Agent — ?Agent — ?Agent        — ?
?  ???????? ???????? ???????? ?????????????? ?
???????????????????????????????????????????????
?      —        —        —                     ?
?  ??????????????????????????????????          ?
?  —         Providers              —          ?
?  —  Chat  —  Image  —  Video      —          ?
?  — Provider?Provider?Provider   —          ?
?  —  Mock  —  Mock   —  Mock      —          ?
?  ??????????????????????????????????          ?
?      —        —        —                     ?
?  ??????????????????????????????????          ?
?  —   HTTP Client (httpx)          —          ?
?  —   with retry & rate limiting   —          ?
?  ??????????????????????????????????          ?
???????????????????????????????????????????????
?              Data Models                     ?
?  Pydantic v2 — Chat, Image, Video, Scene     ?
???????????????????????????????????????????????
?         Agnes AI API (REST)                  ?
???????????????????????????????????????????????
```

---

## Development

```bash
# Set up
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# With coverage
pytest --cov=src tests/

# Lint and format
ruff check src/
ruff format src/

# Type checking
mypy src/
```

### Test Structure

- **Unit tests** — test providers, agents, and models with mock implementations
- **Integration tests** (marked pytest.mark.integration) — require a real API key
- **E2E tests** (marked pytest.mark.e2e) — full pipeline tests

---

## Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Make your changes
4. Run tests and linting (pytest tests/ && ruff check src/)
5. Commit with conventional commit messages
6. Open a Pull Request

---

## License

GPL-3.0 — see LICENSE for details.
