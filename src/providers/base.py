"""Abstract base classes and shared HTTP logic for all providers."""

from __future__ import annotations

import asyncio
from typing import Any, ClassVar, TypeVar

import httpx

from src.config import Settings, get_settings
from src.exceptions import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderServerError,
    ProviderTimeoutError,
)
from src.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseProvider:
    """Abstract base class for all API providers.

    Provides shared HTTP client management, retry logic, and error handling.
    """

    # Subclasses should override these
    PROVIDER_TYPE: ClassVar[str] = "base"
    DEFAULT_MODEL: ClassVar[str] = ""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: httpx.AsyncClient | None = None
        self._logger = get_logger(f"agnes.{self.PROVIDER_TYPE}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.settings.base_url,
                timeout=httpx.Timeout(self.settings.timeout),
                headers=self._build_headers(),
            )
        return self._client

    def _build_headers(self) -> dict[str, str]:
        """Build common HTTP headers for API requests."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        json_data: dict[str, Any] | None = None,
        max_retries: int | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with automatic retry on transient errors.

        Args:
            method: HTTP method ("GET", "POST", etc.).
            url: Request URL path (relative to base_url).
            json_data: Optional JSON body.
            max_retries: Override max retries for this request.

        Returns:
            The HTTP response on success.

        Raises:
            ProviderAuthenticationError: On 401.
            ProviderRateLimitError: On 429 and retries exhausted.
            ProviderServerError: On 5xx and retries exhausted.
            ProviderRequestError: On network errors.
            ProviderTimeoutError: On timeout.
            ProviderResponseError: On unexpected status codes.
        """
        client = await self._get_client()
        retries = max_retries if max_retries is not None else self.settings.max_retries
        last_error: Exception | None = None

        for attempt in range(retries + 1):
            try:
                response = await client.request(method, url, json=json_data)

                if response.status_code == 200:
                    return response

                if response.status_code == 401:
                    raise ProviderAuthenticationError(
                        "Authentication failed. Check your API key."
                    )
                if response.status_code == 429:
                    if attempt < retries:
                        wait = min(2 ** attempt * 2, 30)
                        self._logger.warning(
                            "Rate limited (attempt %d/%d). Waiting %ds.",
                            attempt + 1, retries + 1, wait,
                        )
                        await asyncio.sleep(wait)
                        continue
                    raise ProviderRateLimitError("Rate limit exceeded after all retries.")
                if 500 <= response.status_code < 600:
                    if attempt < retries:
                        wait = min(2 ** attempt * 2, 30)
                        self._logger.warning(
                            "Server error %d (attempt %d/%d). Waiting %ds.",
                            response.status_code, attempt + 1, retries + 1, wait,
                        )
                        await asyncio.sleep(wait)
                        continue
                    raise ProviderServerError(
                        f"Server error {response.status_code} after all retries."
                    )

                raise ProviderResponseError(
                    f"Unexpected status code: {response.status_code} - {response.text[:200]}"
                )

            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                last_error = ProviderTimeoutError(f"Request timed out: {e}")
                if attempt < retries:
                    wait = min(2 ** attempt * 2, 10)
                    self._logger.warning(
                        "Timeout (attempt %d/%d). Waiting %ds.", attempt + 1, retries + 1, wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise last_error from None

            except httpx.HTTPError as e:
                last_error = ProviderRequestError(f"HTTP request failed: {e}")
                if attempt < retries:
                    wait = min(2 ** attempt * 2, 10)
                    self._logger.warning(
                        "HTTP error (attempt %d/%d). Waiting %ds.", attempt + 1, retries + 1, wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise last_error from None

        # Should not reach here, but just in case
        raise ProviderResponseError("Request failed after all retries.")

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> BaseProvider:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


def create_provider(provider_type: str, settings: Settings | None = None) -> BaseProvider:
    """Factory function to create a provider by type name.

    Args:
        provider_type: One of "chat", "image", "video".
        settings: Optional Settings instance.

    Returns:
        An appropriate provider instance.

    Raises:
        ProviderNotFoundError: If provider_type is unknown.
    """
    from src.exceptions import ProviderNotFoundError

    if provider_type == "chat":
        from src.providers.mock_chat import MockChatProvider
        return MockChatProvider(settings)
    elif provider_type == "image":
        from src.providers.mock_image import MockImageProvider
        return MockImageProvider(settings)
    elif provider_type == "video":
        from src.providers.mock_video import MockVideoProvider
        return MockVideoProvider(settings)
    else:
        raise ProviderNotFoundError(f"Unknown provider type: {provider_type}")
