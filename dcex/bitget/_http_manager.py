"""Bitget synchronous HTTP manager."""

import base64
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import parse_qsl, urlencode

import requests

from .._native_http import NativeResponse, load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

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


def _sign(
    timestamp: str,
    method: str,
    path: str,
    query_string: str,
    body: str,
    api_secret: str,
) -> str:
    request_path = f"{path}?{query_string}" if query_string else path
    payload = f"{timestamp}{method.upper()}{request_path}{body}"
    digest = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


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
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "BitgetHttpClient", None)
        if self.use_native and native_client_type is not None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                passphrase=self.passphrase,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BITGET)
            if self._native_client is not None:
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is requests.Session
        )

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bitget private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bitget native client is required for private methods.")
        try:
            status, headers, body = self._native_client.private_request(method_name, params)
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

    def _headers(
        self,
        method: str,
        path: str,
        query_string: str,
        body: str,
        signed: bool,
    ) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "locale": "en-US"}
        if not signed:
            return headers
        if not (self.api_key and self.api_secret and self.passphrase):
            raise ValueError("Signed Bitget requests require api_key, api_secret, and passphrase.")
        timestamp = str(int(time.time() * 1000))
        headers.update(
            {
                "ACCESS-KEY": self.api_key,
                "ACCESS-SIGN": _sign(
                    timestamp,
                    method,
                    path,
                    query_string,
                    body,
                    self.api_secret,
                ),
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": self.passphrase,
            }
        )
        return headers

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """Make an HTTP request to Bitget REST APIs."""
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

        response = None
        try:
            self._log_request(method, url)
            if self._uses_native_transport():
                if signed and not (self.api_key and self.api_secret and self.passphrase):
                    raise ValueError(
                        "Signed Bitget requests require api_key, api_secret, and passphrase."
                    )
                params = parse_qsl(query_string, keep_blank_values=True) if query_string else []
                status, response_headers, response_body = cast(
                    Any,
                    self._native_client,
                ).request_raw(
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
            else:
                headers = self._headers(method, request_path, query_string, body, signed)
                method_upper = method.upper()
                if method_upper == "GET":
                    response = self.session.get(url, headers=headers, timeout=self.timeout)
                elif method_upper == "POST":
                    response = self.session.post(
                        url,
                        headers=headers,
                        data=body,
                        timeout=self.timeout,
                    )
                elif method_upper == "PUT":
                    response = self.session.put(
                        url,
                        headers=headers,
                        data=body,
                        timeout=self.timeout,
                    )
                elif method_upper == "DELETE":
                    response = self.session.delete(url, headers=headers, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
        except (requests.RequestException, RuntimeError) as exc:
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

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
