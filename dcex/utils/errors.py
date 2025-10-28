"""Custom exception classes for API and request handling."""

from typing import Protocol


class ResponseProtocol(Protocol):
    """Protocol for response objects with status_code and text attributes."""

    status_code: int
    text: str


class APIRequestError(Exception):
    """Base exception for API request errors."""

    def __init__(
        self,
        request: str,
        message: str,
        status_code: str | int | None = None,
        time: str | None = None,
        resp_headers: dict | None = None,
    ) -> None:
        self.request = request
        self.message = message
        self.status_code = status_code if status_code is not None else "Unknown"
        self.time = time if time is not None else "Unknown"
        self.resp_headers = resp_headers
        super().__init__(
            f"{message} (ErrCode: {self.status_code}) (ErrTime: {self.time}).\nRequest → {request}."
        )


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
