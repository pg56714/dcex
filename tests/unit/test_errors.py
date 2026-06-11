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
