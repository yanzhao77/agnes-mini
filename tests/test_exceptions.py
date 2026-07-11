"""Tests for the exception hierarchy."""

from src.exceptions import (
    AgentError,
    AgnesMiniError,
    ApiKeyMissingError,
    ChatProviderError,
    ConfigError,
    DownloadError,
    FileNotFoundError,
    ImageGenerationError,
    ImageProviderError,
    IntentRecognitionError,
    OrchestratorError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderNotFoundError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderServerError,
    ProviderTimeoutError,
    ResourceError,
    ToolExecutionError,
    VideoCreationError,
    VideoPollingError,
    VideoProviderError,
    VideoTimeoutError,
)


def test_all_exceptions_inherit_from_agnes_mini_error():
    """All custom exceptions should inherit from AgnesMiniError."""
    exceptions = [
        AgnesMiniError(),
        ConfigError(),
        ApiKeyMissingError(),
        ProviderError(),
        ProviderNotFoundError(),
        ProviderAuthenticationError(),
        ProviderRateLimitError(),
        ProviderServerError(),
        ProviderRequestError(),
        ProviderTimeoutError(),
        ProviderResponseError(),
        ChatProviderError(),
        ImageProviderError(),
        ImageGenerationError(),
        VideoProviderError(),
        VideoCreationError(),
        VideoPollingError(),
        VideoTimeoutError(),
        AgentError(),
        OrchestratorError(),
        IntentRecognitionError(),
        ToolExecutionError(),
        ResourceError(),
        FileNotFoundError(),
        DownloadError(),
    ]
    for exc in exceptions:
        assert isinstance(exc, AgnesMiniError), f"{type(exc).__name__} is not an AgnesMiniError"


def test_exception_can_be_raised_and_caught():
    """All exception types can be raised and caught as AgnesMiniError."""
    try:
        raise ProviderRateLimitError("Rate limited")
    except AgnesMiniError as e:
        assert str(e) == "Rate limited"
    except Exception:
        raise AssertionError("Should have been caught as AgnesMiniError") from None


def test_exception_inheritance_chain():
    """Verify the inheritance chain for key exceptions."""
    assert issubclass(ConfigError, AgnesMiniError)
    assert issubclass(ApiKeyMissingError, ConfigError)
    assert issubclass(ProviderError, AgnesMiniError)
    assert issubclass(ProviderNotFoundError, ProviderError)
    assert issubclass(ProviderAuthenticationError, ProviderError)
    assert issubclass(ProviderRateLimitError, ProviderError)
    assert issubclass(ProviderServerError, ProviderError)
    assert issubclass(ProviderRequestError, ProviderError)
    assert issubclass(ProviderTimeoutError, ProviderError)
    assert issubclass(ProviderResponseError, ProviderError)
    assert issubclass(ImageProviderError, ProviderError)
    assert issubclass(ImageGenerationError, ImageProviderError)
    assert issubclass(VideoProviderError, ProviderError)
    assert issubclass(VideoCreationError, VideoProviderError)
    assert issubclass(VideoPollingError, VideoProviderError)
    assert issubclass(VideoTimeoutError, VideoProviderError)
    assert issubclass(AgentError, AgnesMiniError)
    assert issubclass(OrchestratorError, AgentError)
    assert issubclass(ToolExecutionError, AgentError)
    assert issubclass(ResourceError, AgnesMiniError)


def test_exception_with_message():
    """Exception should preserve the message string."""
    msg = "Something went wrong"
    exc = ProviderError(msg)
    assert str(exc) == msg
    assert exc.args[0] == msg


def test_exception_without_message():
    """Exception can be created without a message."""
    exc = ProviderError()
    assert str(exc) == ""


def test_exception_subclass_count():
    """Verify we have the expected number of exception classes."""
    exception_classes = [
        AgnesMiniError,
        ConfigError,
        ApiKeyMissingError,
        ProviderError,
        ProviderNotFoundError,
        ProviderAuthenticationError,
        ProviderRateLimitError,
        ProviderServerError,
        ProviderRequestError,
        ProviderTimeoutError,
        ProviderResponseError,
        ChatProviderError,
        ImageProviderError,
        ImageGenerationError,
        VideoProviderError,
        VideoCreationError,
        VideoPollingError,
        VideoTimeoutError,
        AgentError,
        OrchestratorError,
        IntentRecognitionError,
        ToolExecutionError,
        ResourceError,
        FileNotFoundError,
        DownloadError,
    ]
    assert len(exception_classes) == 25
    # IntentRecognitionError should be an OrchestratorError
    assert issubclass(IntentRecognitionError, OrchestratorError)
    # ToolExecutionError should be an AgentError
    assert issubclass(ToolExecutionError, AgentError)
