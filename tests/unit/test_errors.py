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
