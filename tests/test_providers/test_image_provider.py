"""Tests for the ImageProvider (mock + real)."""

from __future__ import annotations

import pytest

from src.models.common import ImageSize
from src.models.image import (
    ImageRequest,
    ImageToImageRequest,
    MultiImageCompositionRequest,
)
from src.providers.mock_image import MockImageProvider


@pytest.fixture
def mock_image():
    return MockImageProvider()


@pytest.mark.asyncio
async def test_mock_text_to_image(mock_image):
    request = ImageRequest(prompt="A cat")
    response = await mock_image.text_to_image(request)
    assert len(response.data) > 0
    assert response.data[0].url is not None
    assert "mock.agnes.ai" in response.data[0].url


@pytest.mark.asyncio
async def test_mock_text_to_image_with_size(mock_image):
    request = ImageRequest(prompt="A dog", size=ImageSize.LANDSCAPE_1920)
    response = await mock_image.text_to_image(request)
    assert len(response.data) == 1


@pytest.mark.asyncio
async def test_mock_text_to_image_multiple(mock_image):
    request = ImageRequest(prompt="Birds", n=3)
    response = await mock_image.text_to_image(request)
    assert len(response.data) == 3


@pytest.mark.asyncio
async def test_mock_text_to_image_result(mock_image):
    request = ImageRequest(prompt="Sunset")
    result = await mock_image.text_to_image_result(request)
    assert len(result.urls) > 0
    assert result.revised_prompt is not None
    assert result.model == "agnes-image-2.1-flash"


@pytest.mark.asyncio
async def test_mock_image_to_image(mock_image):
    request = ImageToImageRequest(
        prompt="Make it better",
        image="https://example.com/input.png",
    )
    response = await mock_image.image_to_image(request)
    assert len(response.data) > 0


@pytest.mark.asyncio
async def test_mock_multi_image_composition(mock_image):
    request = MultiImageCompositionRequest(
        prompt="Combine these",
        images=["img1.png", "img2.png"],
    )
    response = await mock_image.multi_image_composition(request)
    assert len(response.data) > 0


@pytest.mark.asyncio
async def test_mock_download_image(mock_image):
    result = await mock_image.download_image("https://example.com/img.png", "./output/test.png")
    assert result == "./output/test.png"


@pytest.mark.asyncio
async def test_mock_generate_and_save(mock_image):
    request = ImageRequest(prompt="Save me")
    result = await mock_image.generate_and_save(request, "./output")
    assert len(result.local_paths) > 0
    assert "mock_image" in result.local_paths[0]
