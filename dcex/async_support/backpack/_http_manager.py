"""Backpack asynchronous HTTP manager."""

import json
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import urlencode

from ..._native_http import NativeResponse, load_native, native_body_text, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()

RequestPayload = Mapping[str, Any] | Sequence[Mapping[str, Any]]


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _filtered_query(query: Mapping[str, Any] | None) -> dict[str, Any]:
    return {key: value for key, value in (query or {}).items() if value is not None}


def _encoded_query(query: Mapping[str, Any], *, sort: bool = False) -> str:
    items = sorted(query.items()) if sort else query.items()
    return urlencode(
        [(key, _format_value(value)) for key, value in items],
        doseq=True,
    )


def _json_body(query: RequestPayload | None) -> str:
    if query is None:
        return ""
    return json.dumps(query, separators=(",", ":"), ensure_ascii=False)


def _native_items(payload: Mapping[str, Any]) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for key, value in _filtered_query(payload).items():
        if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
            items.extend((key, _format_value(item)) for item in value)
        else:
            items.append((key, _format_value(value)))
    return items


def _native_signature_payload(
    payload: RequestPayload | None,
) -> list[list[tuple[str, str]]] | None:
    if payload is None:
        return None
    if isinstance(payload, Mapping):
        return [_native_items(payload)]
    return [_native_items(item) for item in payload]


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Backpack REST APIs."""

    EXCHANGE = Common.BACKPACK

    base_url: str = field(default="https://api.backpack.exchange")
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    window: int = field(default=5000)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "BackpackHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                window=self.window,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BACKPACK)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Backpack public method and decode its JSON body."""
        if self._native_client is None:
            await self.async_init()
        if self._native_client is None:
            raise RuntimeError("Backpack native client is required for public methods.")
        if not hasattr(self._native_client, "public_request_json_async"):
            raise RuntimeError("Backpack native client public_request_json_async is unavailable.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "public_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BACKPACK {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Backpack private method and decode its JSON body."""
        if self._native_client is None:
            await self.async_init()
        if self._native_client is None:
            raise RuntimeError("Backpack native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_json_async"):
            raise RuntimeError("Backpack native client private_request_json_async is unavailable.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BACKPACK {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            if key in {"from_", "type_"}:
                key = key.removesuffix("_")
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                params.append((key, str(value).lower()))
            elif isinstance(value, Mapping):
                params.append((key, _json_body(value)))
            elif isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
                if key == "orders":
                    params.append((key, _json_body(value)))
                else:
                    params.extend(
                        (key, _format_value(getattr(item, "value", item))) for item in value
                    )
            else:
                params.append((key, _format_value(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST", "PATCH", "DELETE"],
        path: str,
        query: RequestPayload | None = None,
        signed: bool = False,
        instruction: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Make an HTTP request to Backpack REST APIs."""
        if self._native_client is None:
            await self.async_init()

        request_path = str(path)
        method_upper = method.upper()
        url = f"{self.base_url}{request_path}"
        query_payload = query if isinstance(query, Mapping) else None
        body_payload = query if method_upper in {"POST", "PATCH", "DELETE"} else None
        query_string = (
            _encoded_query(_filtered_query(query_payload))
            if method_upper == "GET" and query_payload is not None
            else ""
        )
        if query_string:
            url = f"{url}?{query_string}"
        body = _json_body(body_payload) if body_payload is not None else None
        signed_payload = body_payload if body_payload is not None else query_payload
        self._uses_native_transport()
        if signed:
            if not self.api_key or not self.api_secret:
                raise ValueError("Signed Backpack requests require api_key and api_secret.")
            if not instruction:
                raise ValueError("Signed Backpack requests require an instruction.")

        try:
            self._log_request(method, url)
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_json_async(
                method,
                request_path,
                _native_items(query_payload) if query_payload is not None else [],
                body.encode() if body is not None else None,
                signed,
                instruction,
                _native_signature_payload(signed_payload),
                {key: value for key, value in (headers or {}).items() if value},
            )
            response = NativeResponse(status, dict(response_headers))
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc

        self._store_response_headers(response)
        data = response_body
        if response.status_code // 100 != 2:
            message = native_body_text(data)
            if isinstance(data, dict):
                message = str(data.get("message") or data.get("code") or native_body_text(data))
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {message}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )

        return data

    async def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
