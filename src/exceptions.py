"""Agnes Mini exception hierarchy.

All exceptions inherit from AgnesMiniError for clean error handling.
"""


class AgnesMiniError(Exception):
    """Base exception for all Agnes Mini errors."""


# --- Configuration errors ---

class ConfigError(AgnesMiniError):
    """Raised when there is a configuration issue."""


class ApiKeyMissingError(ConfigError):
    """Raised when no API key is configured and a real provider is requested."""


# --- Provider errors ---

class ProviderError(AgnesMiniError):
    """Base exception for provider-related errors."""


class ProviderNotFoundError(ProviderError):
    """Raised when an unknown provider type is requested."""


class ProviderAuthenticationError(ProviderError):
    """Raised when API authentication fails (401)."""


class ProviderRateLimitError(ProviderError):
    """Raised when API rate limit is exceeded (429)."""


class ProviderServerError(ProviderError):
    """Raised when the API returns a server error (5xx)."""


class ProviderRequestError(ProviderError):
    """Raised when the request fails due to network issues."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""


class ProviderResponseError(ProviderError):
    """Raised when the API response is invalid or unexpected."""


# --- Chat provider errors ---

class ChatProviderError(ProviderError):
    """Base exception for chat provider errors."""


# --- Image provider errors ---

class ImageProviderError(ProviderError):
    """Base exception for image provider errors."""


class ImageGenerationError(ImageProviderError):
    """Raised when image generation fails."""


# --- Video provider errors ---

class VideoProviderError(ProviderError):
    """Base exception for video provider errors."""


class VideoCreationError(VideoProviderError):
    """Raised when video task creation fails."""


class VideoPollingError(VideoProviderError):
    """Raised when video polling fails."""


class VideoTimeoutError(VideoProviderError):
    """Raised when video generation times out."""


# --- Agent errors ---

class AgentError(AgnesMiniError):
    """Base exception for agent-related errors."""


class AgentExecutionError(AgentError):
    """Raised when an agent fails to execute a task."""


class OrchestratorError(AgentError):
    """Base exception for orchestrator errors."""


class IntentRecognitionError(OrchestratorError):
    """Raised when intent cannot be determined from user input."""


class ToolExecutionError(AgentError):
    """Raised when a tool call fails."""


# --- Resource errors ---

class ResourceError(AgnesMiniError):
    """Base exception for resource-related errors."""


class FileNotFoundError(ResourceError):
    """Raised when a required file is not found."""


class DownloadError(ResourceError):
    """Raised when a file download fails."""
