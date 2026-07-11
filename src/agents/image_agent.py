"""Image agent wrapping ImageProvider with local caching."""
from __future__ import annotations
from typing import Any
from src.agents.base import BaseAgent
from src.models.image import ImageGenerationResult, ImageRequest
from src.models.common import ImageSize
from src.providers.image import ImageProvider
from src.providers.mock_image import MockImageProvider


class ImageAgent(BaseAgent):
    """Agent for image generation."""
    AGENT_TYPE = "image"

    def __init__(self, settings: Any = None) -> None:
        super().__init__(settings)
        self._provider: ImageProvider | MockImageProvider = (
            ImageProvider(self.settings) if not self.settings.is_mock_mode
            else MockImageProvider(self.settings)
        )

    async def generate(self, prompt: str, size: str | None = None) -> ImageGenerationResult:
        request = ImageRequest(
            model=self.settings.image_model,
            prompt=prompt,
            size=ImageSize(size) if size else None,
        )
        return await self._provider.text_to_image_result(request)

    async def generate_and_save(self, prompt: str, output_dir: str | None = None) -> ImageGenerationResult:
        request = ImageRequest(model=self.settings.image_model, prompt=prompt)
        return await self._provider.generate_and_save(request, output_dir)

    async def image_to_image(self, prompt: str, image_url: str) -> ImageGenerationResult:
        from src.models.image import ImageToImageRequest
        request = ImageToImageRequest(
            model=self.settings.image_model, prompt=prompt, image=image_url
        )
        resp = await self._provider.image_to_image(request)
        return ImageGenerationResult(
            urls=[d.url for d in resp.data if d.url],
            model=self.settings.image_model,
        )
