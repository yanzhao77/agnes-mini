# Agnes Mini — Agnes AI API 轻量 Python SDK

通过 Agnes AI API 实现对话聊天、图像生成、视频生成，以及剧本转视频的完整管道。

## 使用场景

- 调用 Agnes AI 大模型进行对话/聊天
- 生成图像（文生图、图生图、多图合成）
- 生成视频（异步任务创建 + 轮询获取结果）
- 将叙事剧本自动分解为多镜头视频（角色/场景一致性保持）

## 环境要求

- Python 3.10+
- 已安装 agnes-mini 包（`pip install -e .` 或 `pip install -e ".[cli]"`）
- 可选：Agnes AI API Key（不填则自动使用 Mock 模式）

## 配置

在项目根目录创建 `.env` 文件：

```ini
AGNES_API_KEY=sk-your-key-here
AGNES_BASE_URL=https://api.agnesai.com
```

不配置 API Key 时自动进入 Mock 模式，所有功能均可在无真实 API 的情况下开发和测试。

## 可用工具

### agnes_run(prompt: str) -> AgentResult

接收自然语言 prompt，自动识别意图并路由到对应的 Agent：

- "法国的首都是哪里？" → 对话
- "生成一张赛博朋克城市图片" → 图像生成
- "生成一个海浪视频" → 视频生成
- "将以下剧本分解为镜头并生成视频：..." → 剧本转视频管道

返回 AgentResult，包含 text、image_urls、video_urls 字段。

### get_available_tools() -> list[str]

返回当前可用的工具列表：["chat", "generate_image", "generate_video"]

## 触发关键词

| 关键词 | 触发行为 |
|--------|----------|
| agnes / Agnes AI | 唤醒 Agnes Mini 技能 |
| 生成图片 / 生成图像 | 调用图像生成 |
| 生成视频 | 调用视频生成 |
| 对话 / 聊天 / AI 聊天 | 调用对话补全 |
| 剧本转视频 / 视频管道 / 脚本转视频 | 调用完整视频管道 |

## 示例

```python
from src.skill import agnes_run

# 简单对话
result = await agnes_run("你好，请介绍一下你自己")
print(result.text)

# 生成图像
result = await agnes_run("生成一张夕阳下的山景图")
print(result.image_urls)

# 生成视频
result = await agnes_run("生成一个无人机航拍未来城市的视频")
print(result.video_urls)
```

## 注意事项

- 视频生成是异步任务，首次调用可能等待 1-5 分钟
- Mock 模式无需 API Key，适合开发和测试
- 生产环境请配置有效的 API Key
