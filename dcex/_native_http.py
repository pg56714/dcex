"""Helpers shared by Python managers using the Rust HTTP core."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import Any


def load_native() -> ModuleType:
    """Load the required PyO3 module."""
    try:
        return import_module("dcex._native")
    except ImportError as exc:
        raise RuntimeError("The dcex native extension is required.") from exc


@dataclass(frozen=True)
class NativeResponse:
    """Adapt Rust response metadata to the Python response interface."""

    status_code: int
    headers: dict[str, str]

    @property
    def ok(self) -> bool:
        """Return whether the HTTP status is below 400."""
        return self.status_code < 400


def native_body_text(body: object) -> str:
    """Format a native JSON response body for error messages."""
    if body is None:
        return ""
    if isinstance(body, str):
        return body
    if isinstance(body, bytes | bytearray | memoryview):
        return bytes(body).decode(errors="replace")
    try:
        return json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        return str(body)


def native_json_response(
    status: int, headers: Mapping[str, str], body: object
) -> tuple[NativeResponse, Any]:
    response = NativeResponse(status, dict(headers))
    return response, body


def _native_method(native_client: Any, method_name: str) -> Any:  # noqa: ANN401
    try:
        return getattr(native_client, method_name)
    except AttributeError as exc:
        raise RuntimeError(f"Native client {method_name} is unavailable.") from exc


def request_native_json(
    native_client: Any,  # noqa: ANN401
    request_method: str,
    method_name: str,
    params: list[tuple[str, str]],
) -> tuple[NativeResponse, Any]:
    """Call a native exchange request and return response metadata plus JSON body."""
    json_method = f"{request_method}_json"
    status, headers, body = _native_method(native_client, json_method)(method_name, params)
    return native_json_response(status, headers, body)


async def request_native_json_async(
    native_client: Any,  # noqa: ANN401
    request_method: str,
    method_name: str,
    params: list[tuple[str, str]],
) -> tuple[NativeResponse, Any]:
    """Call an async native exchange request and return response metadata plus JSON body."""
    json_method = f"{request_method}_json_async"
    status, headers, body = await _native_method(native_client, json_method)(method_name, params)
    return native_json_response(status, headers, body)
