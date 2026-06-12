"""Custom exception classes for API and request handling."""

import re
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

_HTTP_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"})
_URL_PATTERN = re.compile(r"(?:https?:/{1,2}|//)[^\s<>'\"]+", re.IGNORECASE)
_BEARER_TOKEN_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_AUTHORIZATION_PATTERN = re.compile(
    r"""(?ix)
    ["']?\bauthorization\b["']?
    \s*[:=]\s*
    (?:
        '[^']*'
        |
        "[^"]*"
        |
        (?:basic|bearer|digest)\s+[^,\s;}\]]+
        |
        [^,\s;}\]]+
    )
    """
)
_SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    ["']?
    \b(?:
        api[_-]?(?:key|secret)
        |
        access[_-]?key
        |
        secret[_-]?key
        |
        signature
        |
        secret
        |
        passphrase
        |
        password
        |
        authorization
        |
        token
    )\b
    ["']?
    \s*[:=]\s*
    (?:
        '[^']*'
        |
        "[^"]*"
        |
        [^,\s&}\]]+
    )
    """
)


class ResponseProtocol(Protocol):
    """Protocol for response objects with status_code and text attributes."""

    status_code: int
    text: str


def sanitize_url(url: str) -> str:
    """Return a URL without query parameters or fragments."""
    url = url.strip()
    if not url:
        return ""
    url = url.split(maxsplit=1)[0]
    try:
        parsed = urlsplit(url)
    except ValueError:
        return "<redacted-url>"
    if parsed.netloc:
        safe_netloc = parsed.netloc.rsplit("@", 1)[-1]
        return urlunsplit((parsed.scheme, safe_netloc, parsed.path, "", ""))
    if parsed.scheme.lower() in {"http", "https"}:
        return "<redacted-url>"
    return url.split("?", 1)[0].split("#", 1)[0]


def sanitize_message(message: str) -> str:
    """Redact URLs and credential-like assignments from an error message."""

    def replace_url(match: re.Match[str]) -> str:
        matched_url = match.group(0)
        trailing = matched_url[len(matched_url.rstrip(".,;:!?)]}")) :]
        raw_url = matched_url[: len(matched_url) - len(trailing)] if trailing else matched_url
        return f"{sanitize_url(raw_url)}{trailing}"

    sanitized = _URL_PATTERN.sub(replace_url, message)
    sanitized = _AUTHORIZATION_PATTERN.sub("<redacted>", sanitized)
    sanitized = _BEARER_TOKEN_PATTERN.sub("<redacted>", sanitized)
    return _SENSITIVE_ASSIGNMENT_PATTERN.sub("<redacted>", sanitized)


def _sanitize_request(request: str) -> str:
    """Return a request summary without query parameters or payload data."""
    request_line = request.partition(" | ")[0].strip()
    method, separator, url = request_line.partition(" ")
    method = method.upper()
    if not separator or method not in _HTTP_METHODS:
        return "<redacted>"

    safe_url = sanitize_url(url)
    if not safe_url:
        return "<redacted>"

    return f"{method} {safe_url}"


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
        self.request = _sanitize_request(request)
        self.message = sanitize_message(message)
        self.status_code = status_code if status_code is not None else "Unknown"
        self.time = time if time is not None else "Unknown"
        self.resp_headers = resp_headers
        super().__init__(
            f"{self.message} (ErrCode: {self.status_code}) (ErrTime: {self.time}).\n"
            f"Request: {self.request}."
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
