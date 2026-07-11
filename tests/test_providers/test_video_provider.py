"""Tests for the VideoProvider (mock + real)."""

from __future__ import annotations

import pytest

from src.exceptions import VideoPollingError
from src.models.common import VideoStatus
from src.models.video import VideoPollConfig, VideoRequest
from src.providers.mock_video import MockVideoProvider


@pytest.fixture
def mock_video():
    return MockVideoProvider()


@pytest.mark.asyncio
async def test_mock_create_task(mock_video):
    request = VideoRequest(prompt="A drone flying")
    response = await mock_video.create_task(request)
    assert response.task_id.startswith("mock-video-task-")
    assert response.status == VideoStatus.PENDING


@pytest.mark.asyncio
async def test_mock_query_task(mock_video):
    request = VideoRequest(prompt="Test")
    created = await mock_video.create_task(request)
    result = await mock_video.query_task(created.task_id)
    assert result.task_id == created.task_id
    assert result.status in (
        VideoStatus.PENDING,
        VideoStatus.PROCESSING,
        VideoStatus.COMPLETED,
    )


@pytest.mark.asyncio
async def test_mock_query_unknown_task(mock_video):
    result = await mock_video.query_task("nonexistent-task")
    assert result.status == VideoStatus.FAILED


@pytest.mark.asyncio
async def test_mock_poll_task(mock_video):
    request = VideoRequest(prompt="Test video")
    created = await mock_video.create_task(request)
    config = VideoPollConfig(interval=1, timeout=30)
    result = await mock_video.poll_task(created.task_id, config)
    assert result.video_url is not None
    assert "mock.agnes.ai" in result.video_url


@pytest.mark.asyncio
async def test_mock_poll_failed_task(mock_video):
    with pytest.raises(VideoPollingError):
        await mock_video.poll_task("nonexistent-task")


@pytest.mark.asyncio
async def test_mock_download_video(mock_video):
    result = await mock_video.download_video(
        "https://mock.agnes.ai/videos/test.mp4", "./output/test.mp4"
    )
    assert result == "./output/test.mp4"


@pytest.mark.asyncio
async def test_mock_create_multiple_tasks(mock_video):
    req1 = VideoRequest(prompt="First")
    req2 = VideoRequest(prompt="Second")
    t1 = await mock_video.create_task(req1)
    t2 = await mock_video.create_task(req2)
    assert t1.task_id != t2.task_id
