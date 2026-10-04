"""Custom exception classes for API and request handling."""

from typing import Protocol

from .. import _native


class ResponseProtocol(Protocol):
    """Protocol for response objects with status_code and text attributes."""

    status_code: int
    text: str


def sanitize_url(url: str) -> str:
    """Return a URL without query parameters or fragments."""
    return _native.sanitize_url(url)


def sanitize_message(message: str) -> str:
    """Redact URLs and credential-like assignments from an error message."""
    return _native.sanitize_message(message)


def _sanitize_request(request: str) -> str:
    """Return a request summary without query parameters or payload data."""
    return _native.sanitize_request(request)


def api_error_message(exchange: str, status: object, code: object, message: object) -> str:
    """Format ``{Exchange} API Error: [{code}] {message} (HTTP {status})`` like Rust does."""
    return _native.api_error_message(
        exchange, _status(status), None if code is None else str(code), str(message)
    )


def api_error_from_body(exchange: str, status: object, body: object) -> str:
    """Format the shared error text from a raw error body (code and message parsed)."""
    return _native.api_error_from_body(exchange, _status(status), str(body))


def _status(status: object) -> int:
    try:
        return int(str(status))
    except ValueError:
        return 0


class APIRequestError(Exception):
    """Base exception for API request errors."""

    def __init__(
        self,
        request: str,
        message: str,
        status_code: str | int | None = None,
        time: str | None = None,
        resp_headers: dict | None = None,
        response_data: object = None,
    ) -> None:
        self.request = _sanitize_request(request)
        self.message = sanitize_message(message)
        # The HTTP status; the message already names the exchange, its code and the status.
        self.status_code = status_code
        self.time = time
        self.resp_headers = resp_headers
        self.response_data = response_data
        when = f" (ErrTime: {time})" if time is not None else ""
        super().__init__(f"{self.message}{when}.\nRequest: {self.request}.")


class FailedRequestError(APIRequestError):
    """Exception raised when a request fails."""

    pass


class InvalidRequestError(APIRequestError):
    """Exception raised when a request is invalid."""

    pass


class APIException(Exception):
    """Exception raised for API-related errors."""

    def __init__(self, response: ResponseProtocol) -> None:
        self.status_code = response.status_code
        self.response = response.text

    def __str__(self) -> str:
        return f"APIException(http status={self.status_code}): response={self.response}"


class RequestException(Exception):
    """Exception raised for request-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"RequestException: {self.message}"


class ParamsException(Exception):
    """Exception raised for parameter-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"ParamsException: {self.message}"
