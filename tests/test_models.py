"""Tests for all data models."""

import pytest
from pydantic import ValidationError

from src.models.chat import (
    ChatHistory,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
    MessageContent,
)
from src.models.common import (
    AspectRatio,
    FinishReason,
    FunctionTool,
    ImageSize,
    Role,
    ToolCall,
    Usage,
    VideoDuration,
    VideoStatus,
)
from src.models.image import (
    ImageData,
    ImageGenerationResult,
    ImageRequest,
    ImageResponse,
    ImageToImageRequest,
    MultiImageCompositionRequest,
)
from src.models.video import (
    VideoPollConfig,
    VideoQueryResponse,
    VideoRequest,
    VideoResult,
    VideoTaskResponse,
)

# --- Enum Tests ---

@pytest.mark.parametrize("role", ["system", "user", "assistant", "tool"])
def test_role_enum(role):
    assert Role(role).value == role


@pytest.mark.parametrize("size", ["1024x1024", "1920x1080", "1080x1920", "1216x832", "832x1216"])
def test_image_size_enum(size):
    assert ImageSize(size).value == size


@pytest.mark.parametrize("ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
def test_aspect_ratio_enum(ratio):
    assert AspectRatio(ratio).value == ratio


@pytest.mark.parametrize("status", ["pending", "processing", "completed", "failed", "cancelled"])
def test_video_status_enum(status):
    assert VideoStatus(status).value == status


@pytest.mark.parametrize("duration", ["5", "10", "15", "25"])
def test_video_duration_enum(duration):
    assert VideoDuration(duration).value == duration


@pytest.mark.parametrize("reason", ["stop", "length", "tool_calls", "content_filter", "error"])
def test_finish_reason_enum(reason):
    assert FinishReason(reason).value == reason


def test_function_tool_creation():
    tool = FunctionTool(
        function={"name": "test_fn", "description": "A test", "parameters": {"type": "object"}}
    )
    assert tool.function.name == "test_fn"


# --- Chat Model Tests ---

def test_chat_message_creation():
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.tool_calls is None


def test_chat_message_with_tool_calls():
    msg = ChatMessage(
        role="assistant",
        content="Let me check that",
        tool_calls=[ToolCall(id="call_1", function={"name": "get_weather", "arguments": "{}"})],
    )
    assert msg.role == "assistant"
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].function.name == "get_weather"


def test_chat_request_basic():
    req = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
    assert req.model == "agnes-2.0-flash"
    assert len(req.messages) == 1
    assert not req.stream


def test_chat_request_with_options():
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="Hi")],
        temperature=0.7,
        max_tokens=100,
        stream=True,
    )
    assert req.temperature == 0.7
    assert req.max_tokens == 100
    assert req.stream


def test_chat_response():
    resp = ChatResponse(
        id="chat_1",
        choices=[{"index": 0, "message": {"role": "assistant", "content": "Hello!"}}],
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    )
    assert resp.id == "chat_1"
    assert len(resp.choices) == 1
    assert resp.choices[0].message.content == "Hello!"
    assert resp.usage.total_tokens == 15


def test_chat_stream_chunk():
    chunk = ChatStreamChunk(
        id="chunk_1",
        choices=[{"index": 0, "delta": {"content": "Hello"}}],
    )
    assert chunk.id == "chunk_1"
    assert chunk.choices[0].delta.content == "Hello"


def test_chat_history_accumulation():
    history = ChatHistory(max_turns=3)
    history.add_message(ChatMessage(role="user", content="Hi"))
    history.add_message(ChatMessage(role="assistant", content="Hello!"))
    assert len(history.messages) == 2


def test_chat_history_max_turns():
    history = ChatHistory(max_turns=3)
    history.add_message(ChatMessage(role="system", content="System"))
    history.add_message(ChatMessage(role="user", content="A"))
    history.add_message(ChatMessage(role="assistant", content="B"))
    history.add_message(ChatMessage(role="user", content="C"))
    assert len(history.messages) == 3
    # System message should be preserved
    assert history.messages[0].content == "System"


def test_chat_history_clear():
    history = ChatHistory(max_turns=10)
    history.add_message(ChatMessage(role="user", content="Hi"))
    history.clear()
    assert len(history.messages) == 0


def test_chat_history_to_api_messages():
    history = ChatHistory(max_turns=10)
    history.add_message(ChatMessage(role="user", content="Hi"))
    history.add_message(ChatMessage(role="assistant", content="Hello"))
    api_msgs = history.to_api_messages()
    assert len(api_msgs) == 2
    assert api_msgs[0]["role"] == "user"
    assert api_msgs[0]["content"] == "Hi"


# --- Image Model Tests ---

def test_image_request_basic():
    req = ImageRequest(prompt="A cat")
    assert req.prompt == "A cat"
    assert req.model == "agnes-image-2.1-flash"
    assert req.n == 1


def test_image_request_with_size():
    req = ImageRequest(prompt="A dog", size=ImageSize.SQUARE_1024)
    assert req.size == ImageSize.SQUARE_1024


def test_image_response():
    resp = ImageResponse(
        created=1234567890,
        data=[{"url": "https://example.com/img.png"}],
    )
    assert len(resp.data) == 1
    assert resp.data[0].url == "https://example.com/img.png"


def test_image_generation_result():
    result = ImageGenerationResult(
        urls=["https://example.com/img.png"],
        model="agnes-image-2.1-flash",
    )
    assert len(result.urls) == 1
    assert result.model == "agnes-image-2.1-flash"


def test_image_to_image_request():
    req = ImageToImageRequest(
        prompt="Make it better",
        image="https://example.com/input.png",
    )
    assert req.image == "https://example.com/input.png"


def test_multi_image_composition():
    req = MultiImageCompositionRequest(
        prompt="Combine these",
        images=["img1.png", "img2.png"],
        mode="composition",
    )
    assert len(req.images) == 2
    assert req.mode == "composition"


# --- Video Model Tests ---

def test_video_request_basic():
    req = VideoRequest(prompt="A flying drone")
    assert req.prompt == "A flying drone"
    assert req.model == "agnes-video-v2.0"


def test_video_request_with_options():
    req = VideoRequest(
        prompt="A flying drone",
        duration=VideoDuration.MEDIUM,
        aspect_ratio=AspectRatio.LANDSCAPE_16_9,
        image_url="https://example.com/frame.png",
    )
    assert req.duration == VideoDuration.MEDIUM
    assert req.aspect_ratio == AspectRatio.LANDSCAPE_16_9
    assert req.image_url == "https://example.com/frame.png"


def test_video_task_response():
    resp = VideoTaskResponse(task_id="task_1", video_id="vid_1", status=VideoStatus.PENDING)
    assert resp.task_id == "task_1"
    assert resp.video_id == "vid_1"
    assert resp.status == VideoStatus.PENDING


def test_video_query_response():
    resp = VideoQueryResponse(
        id="q_1",
        task_id="task_1",
        status=VideoStatus.PROCESSING,
        progress=50,
    )
    assert resp.status == VideoStatus.PROCESSING
    assert resp.progress == 50


def test_video_query_completed():
    resp = VideoQueryResponse(
        id="q_1",
        task_id="task_1",
        status=VideoStatus.COMPLETED,
        video_url="https://example.com/video.mp4",
        progress=100,
    )
    assert resp.video_url == "https://example.com/video.mp4"


def test_video_result():
    result = VideoResult(video_url="https://example.com/video.mp4", task_id="task_1")
    assert result.video_url == "https://example.com/video.mp4"
    assert result.task_id == "task_1"


def test_video_poll_config():
    config = VideoPollConfig(interval=3, timeout=300)
    assert config.interval == 3
    assert config.timeout == 300
    assert config.max_retries == 3


def test_video_poll_config_validation():
    with pytest.raises(ValidationError):
        VideoPollConfig(interval=0)


# --- Usage Model Tests ---

def test_usage_defaults():
    usage = Usage()
    assert usage.prompt_tokens == 0
    assert usage.completion_tokens == 0
    assert usage.total_tokens == 0


def test_usage_with_values():
    usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    assert usage.total_tokens == 150


def test_message_content():
    content = MessageContent(type="text", text="Hello")
    assert content.text == "Hello"


def test_tool_call_creation():
    tc = ToolCall(id="call_abc", function={"name": "test_fn", "arguments": '{"key": "val"}'})
    assert tc.id == "call_abc"
    assert tc.function.name == "test_fn"


def test_model_serialization():
    """Test that models serialize correctly to dict."""
    msg = ChatMessage(role="user", content="Hello")
    d = msg.model_dump(exclude_none=True)
    assert d["role"] == "user"
    assert d["content"] == "Hello"
    assert "tool_calls" not in d


def test_model_deserialization():
    """Test that models deserialize correctly from dict."""
    data = {"role": "assistant", "content": "World"}
    msg = ChatMessage(**data)
    assert msg.role == "assistant"
    assert msg.content == "World"


def test_image_data_url():
    img = ImageData(url="https://example.com/img.png")
    assert img.url == "https://example.com/img.png"
    assert img.b64_json is None
    assert img.revised_prompt is None


def test_image_data_b64():
    img = ImageData(b64_json="base64encodedstring")
    assert img.b64_json == "base64encodedstring"
    assert img.url is None
