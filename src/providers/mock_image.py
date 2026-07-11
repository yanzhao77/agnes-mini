"""Mock image provider for development and testing without a real API key."""

from __future__ import annotations

from src.models.image import (
    ImageData,
    ImageGenerationResult,
    ImageRequest,
    ImageResponse,
    ImageToImageRequest,
    MultiImageCompositionRequest,
)
from src.providers.base import BaseProvider


class MockImageProvider(BaseProvider):
    """Mock image provider that returns placeholder responses."""

    PROVIDER_TYPE = "mock_image"
    DEFAULT_MODEL = "agnes-image-2.1-flash"

    async def text_to_image(self, request: ImageRequest) -> ImageResponse:
        """Return a mock image generation response."""
        return ImageResponse(
            created=1700000000,
            data=[
                ImageData(
                    url=f"https://mock.agnes.ai/images/{hash(request.prompt)}.png",
                    revised_prompt=f"Enhanced: {request.prompt}",
                )
                for _ in range(request.n)
            ],
        )

    async def text_to_image_result(self, request: ImageRequest) -> ImageGenerationResult:
        """Return a mock image generation result with metadata."""
        resp = await self.text_to_image(request)
        return ImageGenerationResult(
            urls=[d.url for d in resp.data if d.url],
            revised_prompt=resp.data[0].revised_prompt if resp.data else None,
            model=request.model,
            created=resp.created,
        )

    async def image_to_image(self, request: ImageToImageRequest) -> ImageResponse:
        """Return a mock image-to-image response."""
        return ImageResponse(
            created=1700000000,
            data=[
                ImageData(
                    url=f"https://mock.agnes.ai/images/img2img_{hash(request.prompt)}.png",
                )
            ],
        )

    async def multi_image_composition(
        self, request: MultiImageCompositionRequest
    ) -> ImageResponse:
        """Return a mock multi-image composition response."""
        return ImageResponse(
            created=1700000000,
            data=[
                ImageData(
                    url=f"https://mock.agnes.ai/images/compose_{hash(request.prompt)}.png",
                )
            ],
        )

    async def download_image(self, url: str, output_path: str) -> str:
        """Mock download - just return the output path."""
        return output_path

    async def generate_and_save(
        self, request: ImageRequest, output_dir: str | None = None
    ) -> ImageGenerationResult:
        """Generate and 'save' image locally (mock)."""
        result = await self.text_to_image_result(request)
        result.local_paths = [f"{output_dir or './output'}/mock_image.png"]
        return result
