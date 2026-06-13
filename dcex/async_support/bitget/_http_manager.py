"""Bitget asynchronous HTTP manager."""

import base64
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal, Self
from urllib.parse import urlencode

import httpx

from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


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
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITGET)
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

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

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """Make an HTTP request to Bitget REST APIs."""
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session.")

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

        headers = self._headers(method, request_path, query_string, body, signed)
        response = None
        try:
            self._log_request(method, url)
            method_upper = method.upper()
            if method_upper == "GET":
                response = await self.session.get(url, headers=headers)
            elif method_upper == "POST":
                response = await self.session.post(url, headers=headers, content=body)
            elif method_upper == "PUT":
                response = await self.session.put(url, headers=headers, content=body)
            elif method_upper == "DELETE":
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except httpx.RequestError as exc:
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
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
