"""Real ImageProvider for Agnes AI image generation API."""
from __future__ import annotations
from typing import Any, Dict, Optional
from src.models.image import ImageData, ImageGenerationResult, ImageRequest, ImageResponse, ImageToImageRequest, MultiImageCompositionRequest
from src.providers.base import BaseProvider


class ImageProvider(BaseProvider):
    """Provider for Agnes AI image generation API."""
    PROVIDER_TYPE = "image"
    DEFAULT_MODEL = "agnes-image-2.1-flash"

    async def text_to_image(self, request: ImageRequest) -> ImageResponse:
        payload = self._build_image_payload(request)
        response = await self._request_with_retry("POST", "/v1/images/generations", json_data=payload)
        data = response.json()
        return ImageResponse(
            created=data.get("created", 0),
            data=[ImageData(**d) for d in data.get("data", [])],
        )

    async def text_to_image_result(self, request: ImageRequest) -> ImageGenerationResult:
        resp = await self.text_to_image(request)
        return ImageGenerationResult(
            urls=[d.url for d in resp.data if d.url],
            revised_prompt=resp.data[0].revised_prompt if resp.data else None,
            model=request.model,
            created=resp.created,
        )

    async def image_to_image(self, request: ImageToImageRequest) -> ImageResponse:
        payload: Dict[str, Any] = {"model": request.model, "prompt": request.prompt}
        if request.size:
            payload["size"] = request.size.value
        if request.strength is not None:
            payload["strength"] = request.strength
        extra: Dict[str, Any] = dict(request.extra_body or {})
        extra["image"] = request.image
        payload["extra_body"] = extra
        response = await self._request_with_retry("POST", "/v1/images/generations", json_data=payload)
        data = response.json()
        return ImageResponse(
            created=data.get("created", 0),
            data=[ImageData(**d) for d in data.get("data", [])],
        )

    async def multi_image_composition(self, request: MultiImageCompositionRequest) -> ImageResponse:
        payload: Dict[str, Any] = {"model": request.model, "prompt": request.prompt}
        if request.size:
            payload["size"] = request.size.value
        extra: Dict[str, Any] = dict(request.extra_body or {})
        extra["images"] = request.images
        extra["mode"] = request.mode
        payload["extra_body"] = extra
        response = await self._request_with_retry("POST", "/v1/images/generations", json_data=payload)
        data = response.json()
        return ImageResponse(
            created=data.get("created", 0),
            data=[ImageData(**d) for d in data.get("data", [])],
        )

    async def download_image(self, url: str, output_path: str) -> str:
        client = await self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        import aiofiles  # not available, use sync fallback
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path

    async def generate_and_save(self, request: ImageRequest, output_dir: Optional[str] = None) -> ImageGenerationResult:
        result = await self.text_to_image_result(request)
        import os
        out_dir = output_dir or "./output"
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        for i, url in enumerate(result.urls):
            path = os.path.join(out_dir, f"image_{i}.png")
            await self.download_image(url, path)
            paths.append(path)
        result.local_paths = paths
        return result

    def _build_image_payload(self, request: ImageRequest) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": request.model, "prompt": request.prompt, "n": request.n}
        if request.size:
            payload["size"] = request.size.value
        if request.aspect_ratio:
            payload["aspect_ratio"] = request.aspect_ratio.value
        if request.extra_body:
            payload["extra_body"] = request.extra_body
        return payload
