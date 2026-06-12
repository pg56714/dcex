"""Kraken asynchronous HTTP manager."""

import base64
import hashlib
import hmac
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

AuthType = Literal["spot", "futures"]


def _kraken_error_message(data: Any) -> str | None:  # noqa: ANN401
    if not isinstance(data, dict):
        return None

    spot_errors = data.get("error")
    if isinstance(spot_errors, list) and spot_errors:
        return ", ".join(str(error) for error in spot_errors)
    if isinstance(spot_errors, str) and spot_errors:
        return spot_errors

    if data.get("result") == "error":
        futures_errors = data.get("errors") or data.get("error")
        if isinstance(futures_errors, list):
            return ", ".join(str(error) for error in futures_errors)
        if futures_errors:
            return str(futures_errors)
        return "Kraken API error"

    return None


def _filtered_query(query: dict[str, Any] | None) -> dict[str, Any]:
    filtered: dict[str, Any] = {}
    for key, value in (query or {}).items():
        if value is None:
            continue
        filtered[key] = str(value).lower() if isinstance(value, bool) else value
    return filtered


def _encoded_query(query: dict[str, Any]) -> str:
    return urlencode(query, doseq=True)


def _spot_signature(path: str, payload: dict[str, Any], api_secret: str) -> str:
    encoded = _encoded_query(payload)
    message = path.encode() + hashlib.sha256((str(payload["nonce"]) + encoded).encode()).digest()
    mac = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()


def _futures_auth_path(path: str) -> str:
    if path.startswith("/derivatives"):
        return path.removeprefix("/derivatives")
    return path


def _futures_signature(path: str, post_data: str, nonce: str, api_secret: str) -> str:
    auth_path = _futures_auth_path(path)
    hashed = hashlib.sha256((post_data + nonce + auth_path).encode()).digest()
    mac = hmac.new(base64.b64decode(api_secret), hashed, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Kraken public REST APIs."""

    EXCHANGE = Common.KRAKEN

    base_url: str = field(default="https://api.kraken.com")
    futures_base_url: str = field(default="https://futures.kraken.com")
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    spot_api_key: str | None = field(default=None, repr=False)
    spot_api_secret: str | None = field(default=None, repr=False)
    futures_api_key: str | None = field(default=None, repr=False)
    futures_api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self._setup_logger(self.logger)

        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.KRAKEN)
        return self

    @property
    def _spot_api_key(self) -> str | None:
        return self.spot_api_key or self.api_key

    @property
    def _spot_api_secret(self) -> str | None:
        return self.spot_api_secret or self.api_secret

    @property
    def _futures_api_key(self) -> str | None:
        return self.futures_api_key or self.api_key

    @property
    def _futures_api_secret(self) -> str | None:
        return self.futures_api_secret or self.api_secret

    def _infer_auth_type(self, path: str, base_url: str | None) -> AuthType:
        if path.startswith("/derivatives") or base_url == self.futures_base_url:
            return "futures"
        return "spot"

    def _spot_headers(self, path: str, payload: dict[str, Any]) -> dict[str, str]:
        api_key = self._spot_api_key
        api_secret = self._spot_api_secret
        if not api_key or not api_secret:
            raise ValueError(
                "Signed Kraken spot requests require spot_api_key and spot_api_secret."
            )
        return {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Key": api_key,
            "API-Sign": _spot_signature(path, payload, api_secret),
        }

    def _futures_headers(self, path: str, post_data: str, nonce: str) -> dict[str, str]:
        api_key = self._futures_api_key
        api_secret = self._futures_api_secret
        if not api_key or not api_secret:
            raise ValueError(
                "Signed Kraken futures requests require futures_api_key and futures_api_secret."
            )
        return {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "APIKey": api_key,
            "Authent": _futures_signature(path, post_data, nonce, api_secret),
            "Nonce": nonce,
        }

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = False,
        base_url: str | None = None,
        auth_type: AuthType | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to Kraken REST APIs."""
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session")

        request_path = str(path)
        filtered_query = _filtered_query(query)
        selected_auth_type = auth_type or self._infer_auth_type(request_path, base_url)
        encoded_query = _encoded_query(filtered_query)

        if filtered_query:
            request_path = f"{request_path}?{encoded_query}"

        url = f"{base_url or self.base_url}{request_path}"
        response = None
        try:
            self._log_request(method, url)
            body: str | None = None
            headers = {"Accept": "application/json"}
            if signed and selected_auth_type == "spot":
                if method.upper() != "POST":
                    raise ValueError("Signed Kraken spot requests must use POST.")
                nonce = str(time.time_ns())
                spot_payload: dict[str, Any] = {"nonce": nonce}
                spot_payload.update(filtered_query)
                body = _encoded_query(spot_payload)
                headers = self._spot_headers(str(path), spot_payload)
                url = f"{base_url or self.base_url}{path}"
            elif signed and selected_auth_type == "futures":
                nonce = str(time.time_ns())
                body = encoded_query
                headers = self._futures_headers(str(path), encoded_query, nonce)
                if method.upper() in {"GET", "DELETE"} and encoded_query:
                    url = f"{base_url or self.base_url}{path}?{encoded_query}"
                else:
                    url = f"{base_url or self.base_url}{path}"

            method_upper = method.upper()
            if method_upper == "GET":
                response = await self.session.get(url, headers=headers)
            elif method_upper == "POST":
                response = await self.session.post(
                    url,
                    headers=headers,
                    content=body if signed else None,
                    json=None if signed else (filtered_query or None),
                )
            elif method_upper == "PUT":
                response = await self.session.put(
                    url,
                    headers=headers,
                    content=body if signed else None,
                    json=None if signed else (filtered_query or None),
                )
            elif method_upper == "DELETE":
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
        except httpx.RequestError as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {e}",
                status_code=response.status_code if response else "Unknown",
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers) if response else None,
            ) from e
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

            timestamp = str(generate_timestamp(iso_format=True))
            error_message = _kraken_error_message(data)
            if error_message:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"KRAKEN API Error: {error_message}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                )

            if response.status_code // 100 != 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                )

            return data

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
