"""Tests for request error sanitization."""
# ruff: noqa: D103

import pytest

from dcex.utils.errors import FailedRequestError, InvalidRequestError


@pytest.mark.parametrize("error_type", [FailedRequestError, InvalidRequestError])
def test_api_request_errors_redact_query_and_payload(error_type: type[Exception]) -> None:
    error = error_type(
        request=(
            "POST https://api.example.com/v1/order?timestamp=123&signature=secret "
            "| Body: {'api_key': 'private-key', 'quantity': '1'}"
        ),
        message="request failed",
        status_code=400,
    )

    assert error.request == "POST https://api.example.com/v1/order"  # type: ignore[attr-defined]
    rendered = str(error)
    assert "Request: POST https://api.example.com/v1/order." in rendered
    for sensitive_value in ("signature", "secret", "api_key", "private-key", "quantity"):
        assert sensitive_value not in rendered


def test_api_request_error_sanitizes_relative_urls() -> None:
    error = FailedRequestError(
        request="GET /api/v5/account/balance?ccy=BTC#fragment | Params: {'ccy': 'BTC'}",
        message="request failed",
    )

    assert error.request == "GET /api/v5/account/balance"


def test_api_request_error_redacts_unstructured_request() -> None:
    error = FailedRequestError(request="sensitive payload", message="request failed")

    assert error.request == "<redacted>"
    assert "sensitive payload" not in str(error)


def test_api_request_error_ignores_unseparated_trailing_payload() -> None:
    error = FailedRequestError(
        request="POST https://api.example.com/v1/order {'api_key': 'private-key'}",
        message="request failed",
    )

    assert error.request == "POST https://api.example.com/v1/order"
    assert "private-key" not in str(error)


def test_api_request_error_sanitizes_urls_and_credentials_in_message() -> None:
    error = FailedRequestError(
        request="POST https://api.example.com/v1/order?signature=request-secret",
        message=(
            "Request failed: 401 Client Error for url: "
            "https://api.example.com/v1/order?timestamp=1&signature=url-secret; "
            '"api_key": "private-key"; Authorization: Bearer bearer-token'
        ),
    )

    rendered = str(error)
    assert "https://api.example.com/v1/order" in rendered
    for sensitive_value in (
        "request-secret",
        "url-secret",
        "private-key",
        "bearer-token",
        "timestamp",
        "signature",
        "api_key",
    ):
        assert sensitive_value not in rendered


def test_api_request_error_redacts_basic_auth_and_url_credentials() -> None:
    error = FailedRequestError(
        request="GET https://request-user:request-password@api.example.com/private?token=secret",
        message=(
            "failed for https://message-user:message-password@api.example.com/private?token=secret "
            "with Authorization: Basic dXNlcjpwYXNzd29yZA=="
        ),
    )

    rendered = str(error)
    assert "https://api.example.com/private" in rendered
    for sensitive_value in (
        "request-user",
        "request-password",
        "message-user",
        "message-password",
        "dXNlcjpwYXNzd29yZA==",
    ):
        assert sensitive_value not in rendered


def test_api_request_error_redacts_uppercase_url_credentials() -> None:
    error = FailedRequestError(
        request="GET HTTPS://request-user:request-password@api.example.com/private?token=secret",
        message=(
            "failed for HTTPS://message-user:message-password@api.example.com/private?token=secret"
        ),
    )

    rendered = str(error)
    assert "https://api.example.com/private" in rendered
    for sensitive_value in (
        "request-user",
        "request-password",
        "message-user",
        "message-password",
        "secret",
    ):
        assert sensitive_value not in rendered


@pytest.mark.parametrize(
    "url",
    [
        "//user:password@api.example.com/private?token=secret",
        "https:/user:password@api.example.com/private?token=secret",
    ],
)
def test_api_request_error_redacts_credentials_from_nonstandard_urls(url: str) -> None:
    error = FailedRequestError(
        request=f"GET {url}",
        message=f"failed for {url}",
    )

    rendered = str(error)
    for sensitive_value in ("user", "password", "secret"):
        assert sensitive_value not in rendered


def test_api_request_error_handles_malformed_url_without_raising() -> None:
    error = FailedRequestError(
        request="GET https://[invalid?token=request-secret",
        message="failed for https://[invalid?token=message-secret",
    )

    assert error.request == "GET <redacted-url>"
    rendered = str(error)
    assert "<redacted-url>" in rendered
    assert "request-secret" not in rendered
    assert "message-secret" not in rendered
