<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-GPL%20v3-blueviolet" alt="GPL v3">
  <img src="https://img.shields.io/badge/version-2.0.0-blueviolet" alt="Version 2.0.0">
  <img src="https://img.shields.io/badge/coverage-65%25-brightgreen" alt="Coverage 65%+">
  <img src="https://img.shields.io/badge/code%20style-ruff-000000" alt="Ruff">
</p>

<p align="center">
  <strong>Agnes Mini — Agnes AI API 轻量 Python SDK</strong>
  <br>
  对话、图像、视频、剧本转视频管道 — 类型安全、纯异步。
</p>

---

## 特性

- **对话补全** — 流式输出、工具调用、多模态、思维链
- **图像生成** — 文生图、图生图、多图合成
- **视频生成** — 异步任务创建、轮询、自动下载
- **智能路由** — Agent 自动识别意图并分发请求
- **剧本转视频管道** — 剧本分解、角色/场景一致性生成、出片
- **Mock 模式** — 无需 API Key 即可开发测试，零配置运行
- **类型安全** — 全站 Pydantic v2 数据模型
- **纯异步** — 基于 httpx，自动重试 + 限速
- **命令行界面** — 基于 Typer 的 CLI 工具
- **优雅错误处理** — 丰富的异常继承体系

---

## 安装

### 源码安装

```bash
git clone https://github.com/yanzhao77/agnes-mini.git
cd agnes-mini
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 安装 CLI 扩展

```bash
pip install -e ".[cli]"
```

### 安装开发工具

```bash
pip install -e ".[dev]"
```

---

## 快速开始

### 1. 配置 API Key（可跳过，直接使用 Mock 模式）

```bash
cp .env.example .env
```

编辑 .env 填入你的 Key：

```ini
AGNES_API_KEY=sk-your-key-here
AGNES_BASE_URL=https://api.agnesai.com
```

### 2. 对话测试

```python
import asyncio
from src.agents.text_agent import TextAgent

async def main():
    agent = TextAgent()
    response = await agent.chat("你好！请介绍一下你自己")
    print(response.choices[0].message.content)

asyncio.run(main())
```

### 3. 生成图像

```python
import asyncio
from src.agents.image_agent import ImageAgent

async def main():
    agent = ImageAgent()
    result = await agent.generate("赛博朋克风格的夜景城市，霓虹灯光")
    for url in result.urls:
        print(url)

asyncio.run(main())
```

### 4. 使用 CLI

```bash
agnes chat "介绍一下 Agnes AI"
agnes image "日落时分的壮丽山景"
agnes video "无人机飞越未来城市"
agnes run "生成一张戴帽子的猫的图片"
```

> 没有 API Key？以上所有示例在 Mock 模式下零配置即可运行。


---

## Codex 集成

本仓库可直接作为 **Codex 技能/插件** 导入使用，无需额外配置。

### 安装方式

**方式一：从 GitHub 安装（推荐）**

在 Codex 中运行 skill-installer 命令：

```bash
install-skill https://github.com/yanzhao77/agnes-mini
```

**方式二：克隆到本地**

```bash
git clone https://github.com/yanzhao77/agnes-mini.git
cd agnes-mini
pip install -e .
```

然后使用 Codex 打开该项目目录即可自动识别。

### 触发关键词

在 Codex 中输入以下关键词即可唤醒 Agnes Mini：

| 关键词 | 功能 |
|--------|------|
| agnes / Agnes AI | 唤醒技能 |
| 生成图片 / 生成图像 | 调用图像生成 |
| 生成视频 | 调用视频生成 |
| 对话 / 聊天 | 调用对话补全 |
| 剧本转视频 / 脚本转视频 | 调用完整视频管道 |

### Mock 模式

不配置 API Key 时自动进入 Mock 模式，所有功能**无需真实 API 凭据**即可在 Codex 中开发和测试。


---

## 配置项

所有配置项通过环境变量或 .env 文件加载：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| AGNES_API_KEY | "" | API Key（为空则自动进入 Mock 模式） |
| AGNES_BASE_URL | https://api.agnesai.com | API 基础地址 |
| AGNES_CHAT_MODEL | agnes-2.0-flash | 对话模型 |
| AGNES_IMAGE_MODEL | agnes-image-2.1-flash | 图像模型 |
| AGNES_VIDEO_MODEL | agnes-video-v2.0 | 视频模型 |
| AGNES_TIMEOUT | 60 | HTTP 请求超时（秒） |
| AGNES_MAX_RETRIES | 3 | 最大重试次数 |
| AGNES_VIDEO_POLL_INTERVAL | 5 | 视频状态轮询间隔（秒） |
| AGNES_VIDEO_POLL_TIMEOUT | 600 | 视频生成最大等待时间（秒） |
| AGNES_LOG_LEVEL | INFO | 日志级别 |
| AGNES_OUTPUT_DIR | ./output | 文件输出目录 |

---

## Python API

### 对话

```python
from src.models.chat import ChatRequest, ChatMessage
from src.providers.chat import ChatProvider

async def example():
    provider = ChatProvider()
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="你好！")],
        temperature=0.7,
        max_tokens=1024,
    )
    response = await provider.chat(request)
    print(response.choices[0].message.content)
```

**流式输出：**

```python
async for chunk in provider.chat_stream(request):
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**思维链模式：**

```python
request = ChatRequest(
    messages=[ChatMessage(role="user", content="解释一下量子计算")],
    extra_body={"thinking": True},
)
```

### 图像生成

```python
from src.models.image import ImageRequest, ImageSize
from src.providers.image import ImageProvider

async def example():
    provider = ImageProvider()
    request = ImageRequest(
        prompt="秋日宁静的日本庭园",
        n=1,
        size=ImageSize.SIZE_1024x1024,
    )
    response = await provider.text_to_image(request)
    for img in response.data:
        print(f"URL: {img.url}")
```

**图生图：**

```python
from src.models.image import ImageToImageRequest
request = ImageToImageRequest(
    prompt="改成冬季雪景",
    image="https://example.com/summer_garden.jpg",
    strength=0.7,
)
response = await provider.image_to_image(request)
```

**多图合成：**

```python
from src.models.image import MultiImageCompositionRequest
request = MultiImageCompositionRequest(
    prompt="将这些图片合成为一个统一场景",
    images=["https://example.com/bg.jpg", "https://example.com/character.png"],
    mode="composition",
)
response = await provider.multi_image_composition(request)
```

### 视频生成

```python
from src.models.video import VideoRequest, VideoDuration
from src.providers.video import VideoProvider

async def example():
    provider = VideoProvider()
    request = VideoRequest(
        prompt="赛博朋克城市夜景，电影级航拍镜头",
        duration=VideoDuration.SECONDS_5,
    )
    task = await provider.create_task(request)
    print(f"任务 ID: {task.task_id}")
    result = await provider.poll_task(task.task_id)
    print(f"视频 URL: {result.video_url}")
    local_path = await provider.download_video(result.video_url, "./output/video.mp4")
---

## Agent 智能路由

OrchestratorAgent 通过意图识别自动将请求分发到对应的子 Agent：

```python
from src.agents.orchestrator import OrchestratorAgent

async def demo():
    orch = OrchestratorAgent()
    result = await orch.run("法国的首都是哪里？")
    print(result.text)
    result = await orch.run("生成一张宁静湖景图片")
    print(result.image_urls)
    result = await orch.run("生成一个海浪拍打沙滩的视频")
    print(result.video_urls)
```

---

## 剧本转视频管道（v2）

ConsistentPipeline 将叙事剧本自动转换成角色和场景一致的多镜头视频：

```python
import asyncio
from src.pipeline_v2 import ConsistentPipeline

async def main():
    pipeline = ConsistentPipeline()
    script = """标题：最后一颗香料
一位身穿中山装的老人正在除夕夜包饺子。
他的仿生人孙女静静地看着..."""
    result = await pipeline.run(script)
    for shot in result.get("results", []):
        print(f"  镜头 {shot['shot']}: 图片={shot['image']}, 视频={shot['video']}")

asyncio.run(main())
```

**管道流程：**

1. **剧本分析** — LLM 将剧本分解为角色、场景和镜头
2. **参考图生成** — 构建角色库（多视角 + 表情）和场景库（多变体）
3. **一致性生成** — 基于参考图生成风格统一的图片和视频
4. **限速保护** — 自动遵守 API 速率限制
5. **状态持久化** — 每阶段保存中间状态，支持断点续跑

---

## Mock 模式

当 AGNES_API_KEY 为空（或设为 mock）时，所有 Provider 自动降级为 Mock 实现，无需 API 凭据即可完成开发、测试和 CI 集成。

---

## 异常处理

| 异常类 | 触发条件 |
|--------|----------|
| ProviderAuthenticationError | API Key 无效（401） |
| ProviderRateLimitError | 请求频率超限（429） |
| ProviderServerError | 服务端错误（5xx） |
| ProviderTimeoutError | 请求超时 |
| VideoCreationError | 视频任务创建失败 |
| VideoTimeoutError | 视频生成超时 |
| ConfigError | 配置错误 |

所有异常继承自 AgnesMiniError，方便统一捕获。

---

## 架构

```
+-----------------------------+
|          CLI                |
|    (typer - src/cli.py)     |
+-----------------------------+
|          Agents             |
|  Text | Image | Video | Orch |
+-----------------------------+
|        Providers            |
|  Chat | Image | Video | Mock|
+-----------------------------+
|   httpx (自动重试+限速)     |
+-----------------------------+
|    Pydantic v2 Models       |
+-----------------------------+
|    Agnes AI API (REST)      |
+-----------------------------+
```

---

## 开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest tests/ -v
pytest --cov=src tests/
ruff check src/
ruff format src/
mypy src/
```

---

## 许可证

GNU General Public License v3.0 — 详见 LICENSE
