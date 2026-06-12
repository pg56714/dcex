"""Backpack asynchronous HTTP manager."""

import base64
import json
import logging
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import urlencode

import httpx
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

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


def _signature_chunks(instruction: str, payload: RequestPayload | None) -> list[str]:
    if payload is None:
        return [f"instruction={instruction}"]
    if isinstance(payload, Mapping):
        query_string = _encoded_query(_filtered_query(payload), sort=True)
        chunk = f"instruction={instruction}"
        if query_string:
            chunk = f"{chunk}&{query_string}"
        return [chunk]
    return [
        f"instruction={instruction}&{_encoded_query(_filtered_query(item), sort=True)}"
        for item in payload
    ]


def _signature_payload(
    instruction: str,
    payload: RequestPayload | None,
    timestamp: str,
    window: str,
) -> str:
    chunks = _signature_chunks(instruction, payload)
    return f"{'&'.join(chunks)}&timestamp={timestamp}&window={window}"


def _sign(message: str, api_secret: str) -> str:
    seed = base64.b64decode(api_secret)
    key = ECC.construct(curve="Ed25519", seed=cast(Any, seed))
    signature = eddsa.new(key, "rfc8032").sign(message.encode())
    return base64.b64encode(signature).decode()


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
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BACKPACK)
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    def _headers(
        self,
        signed: bool,
        instruction: str | None,
        payload: RequestPayload | None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        headers.update({key: value for key, value in (extra_headers or {}).items() if value})
        if not signed:
            return headers
        if not self.api_key or not self.api_secret:
            raise ValueError("Signed Backpack requests require api_key and api_secret.")
        if not instruction:
            raise ValueError("Signed Backpack requests require an instruction.")

        timestamp = str(int(time.time() * 1000))
        window = str(self.window)
        message = _signature_payload(instruction, payload, timestamp, window)
        headers.update(
            {
                "X-API-Key": self.api_key,
                "X-Signature": _sign(message, self.api_secret),
                "X-Timestamp": timestamp,
                "X-Window": window,
            }
        )
        return headers

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
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session.")

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
        request_headers = self._headers(signed, instruction, signed_payload, headers)

        response = None
        try:
            self._log_request(method, url)
            if method_upper == "GET":
                response = await self.session.get(url, headers=request_headers)
            elif method_upper == "POST":
                response = await self.session.post(url, headers=request_headers, content=body)
            elif method_upper == "PATCH":
                response = await self.session.patch(url, headers=request_headers, content=body)
            elif method_upper == "DELETE":
                response = await self.session.request(
                    method_upper,
                    url,
                    headers=request_headers,
                    content=body,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except httpx.RequestError as exc:
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=response.status_code if response else "Unknown",
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers) if response else None,
            ) from exc

        self._store_response_headers(response)
        try:
            data: dict[str, Any] | list[Any] | str = response.json()
        except Exception:
            data = response.text

        if response.status_code // 100 != 2:
            message = response.text
            if isinstance(data, dict):
                message = str(data.get("message") or data.get("code") or response.text)
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {message}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )

        return data

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
        self.session = None
