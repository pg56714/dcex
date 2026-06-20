"""Bitget asynchronous HTTP manager."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import parse_qsl, urlencode

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _filtered_query(query: dict[str, Any] | list[dict[str, Any]] | None) -> dict[str, Any] | list:
    if isinstance(query, list):
        return [
            {key: value for key, value in item.items() if value is not None}
            if isinstance(item, dict)
            else item
            for item in query
        ]
    return {key: value for key, value in (query or {}).items() if value is not None}


def _encoded_query(query: dict[str, Any]) -> str:
    return urlencode({key: _format_value(value) for key, value in query.items()}, doseq=True)


def _json_body(query: dict[str, Any] | list) -> str:
    return json.dumps(query, separators=(",", ":"), ensure_ascii=False) if query else ""


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Bitget REST APIs."""

    EXCHANGE = Common.BITGET

    base_url: str = field(default="https://api.bitget.com")
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    passphrase: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: Any = field(default=None, init=False, repr=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITGET)
        native_client_type = getattr(_native, "BitgetHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                passphrase=self.passphrase,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if self.preload_product_table and self._native_client is not None:
            self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bitget private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bitget native client is required for private methods.")
        try:
            status, headers, body = await self._native_client.private_request_async(
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BITGET {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """Make an HTTP request to Bitget REST APIs."""
        if self._native_client is None:
            await self.async_init()

        request_path = str(path)
        filtered_query = _filtered_query(query)
        query_string = (
            _encoded_query(filtered_query)
            if method.upper() == "GET" and isinstance(filtered_query, dict)
            else ""
        )
        body = _json_body(filtered_query) if method.upper() != "GET" else ""
        url = f"{self.base_url}{request_path}"
        if query_string:
            url = f"{url}?{query_string}"

        try:
            self._log_request(method, url)
            self._uses_native_transport()
            if signed and not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError(
                    "Signed Bitget requests require api_key, api_secret, and passphrase."
                )
            params = parse_qsl(query_string, keep_blank_values=True) if query_string else []
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
                method,
                request_path,
                params,
                body.encode() if body else None,
                signed,
            )
            response = NativeResponse(
                status,
                dict(response_headers),
                bytes(response_body),
            )
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc
        else:
            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                ) from exc

            if data.get("code") != "00000":
                code = data.get("code", "Unknown")
                message = data.get("msg") or data.get("message") or "Unknown error"
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Bitget API Error: [{code}] {message}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

            if response.status_code // 100 != 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

            return data

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.session = None
