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
    """Adapt a Rust response tuple to the Python response interface."""

    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def ok(self) -> bool:
        """Return whether the HTTP status is below 400."""
        return self.status_code < 400

    @property
    def text(self) -> str:
        """Decode the response body for existing error messages."""
        return self.content.decode(errors="replace")

    def json(self) -> Any:  # noqa: ANN401
        """Decode the response body as JSON."""
        return json.loads(self.content)


def _response_from_json(
    status: int, headers: Mapping[str, str], body: object
) -> tuple[NativeResponse, Any]:
    response = NativeResponse(status, dict(headers), b"")
    return response, body


def _response_from_bytes(
    status: int,
    headers: Mapping[str, str],
    body: bytes | bytearray | memoryview,
) -> tuple[NativeResponse, Any]:
    response = NativeResponse(status, dict(headers), bytes(body))
    return response, response.json()


def request_native_json(
    native_client: Any,  # noqa: ANN401
    request_method: str,
    method_name: str,
    params: list[tuple[str, str]],
) -> tuple[NativeResponse, Any]:
    """Call a native exchange request and return response metadata plus JSON body."""
    json_method = f"{request_method}_json"
    if hasattr(native_client, json_method):
        status, headers, body = getattr(native_client, json_method)(method_name, params)
        return _response_from_json(status, headers, body)
    status, headers, body = getattr(native_client, request_method)(method_name, params)
    return _response_from_bytes(status, headers, body)


async def request_native_json_async(
    native_client: Any,  # noqa: ANN401
    request_method: str,
    method_name: str,
    params: list[tuple[str, str]],
) -> tuple[NativeResponse, Any]:
    """Call an async native exchange request and return response metadata plus JSON body."""
    json_method = f"{request_method}_json_async"
    if hasattr(native_client, json_method):
        status, headers, body = await getattr(native_client, json_method)(method_name, params)
        return _response_from_json(status, headers, body)
    status, headers, body = await getattr(native_client, f"{request_method}_async")(
        method_name, params
    )
    return _response_from_bytes(status, headers, body)
