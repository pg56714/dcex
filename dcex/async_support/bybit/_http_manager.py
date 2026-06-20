"""
Bybit HTTP manager module.

This module provides the HTTPManager class for handling HTTP requests
to the Bybit API, including authentication, request signing, and
response handling.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

HTTP_URL = "https://{SUBDOMAIN}.{DOMAIN}.{TLD}"
SUBDOMAIN_TESTNET = "api-testnet"
SUBDOMAIN_MAINNET = "api"
DOMAIN_MAIN = "bybit"
TLD_MAIN = "com"
_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    HTTP manager for Bybit API requests.

    This class handles HTTP requests to the Bybit API, including:
    - Authentication and request signing
    - Error handling and retries
    - Product table management
    - Session management

    Attributes:
        testnet: Whether to use testnet environment
        domain: API domain
        tld: Top-level domain
        api_key: API key for authentication
        api_secret: API secret for signing
        timeout: Request timeout in seconds
        recv_window: Receive window for requests
        logger: Logger instance
        ptm: Product table manager
        preload_product_table: Whether to preload product table
    """

    EXCHANGE = Common.BYBIT

    testnet: bool = field(default=False)
    domain: str = field(default=DOMAIN_MAIN)
    tld: str = field(default=TLD_MAIN)
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    recv_window: int = field(default=5000)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    sync_server_time: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Returns:
            Self instance for method chaining
        """
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BYBIT)
        subdomain = SUBDOMAIN_TESTNET if self.testnet else SUBDOMAIN_MAINNET
        self.endpoint = HTTP_URL.format(SUBDOMAIN=subdomain, DOMAIN=self.domain, TLD=self.tld)
        native_client_type = getattr(_native, "BybitHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                recv_window=self.recv_window,
                sync_server_time=self.sync_server_time,
                timeout=self.timeout,
                base_url=self.endpoint,
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
        """Call a Rust-backed Bybit private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for private methods.")
        try:
            status, headers, body = await self._native_client.private_request_async(
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BYBIT {method_name} | Params: {params}",
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
                value = str(value)
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to Bybit API.

        Args:
            method: HTTP method (GET or POST)
            path: API endpoint path
            query: Query parameters or request body
            signed: Whether to sign the request

        Returns:
            Dict containing API response data

        Raises:
            RuntimeError: If native initialization fails
            ValueError: If signed request lacks credentials
            FailedRequestError: If request fails or API returns error
        """
        if self._native_client is None:
            await self.async_init()

        if query is None:
            query = {}

        request_path = path
        self._uses_native_transport()
        timestamp = int(generate_timestamp())

        if method.upper() == "GET":
            if query:
                sorted_query = "&".join(
                    f"{k}={v}" for k, v in sorted(query.items()) if v is not None
                )
                path += "?" + sorted_query if sorted_query else ""
                payload = sorted_query
            else:
                payload = ""
        else:
            payload = json.dumps(query, separators=(",", ":"))

        if signed:
            if not (self.api_key and self.api_secret):
                raise ValueError("Signed request requires API Key and Secret.")

        url = self.endpoint + path
        self._log_request(method, url)

        try:
            params = [
                (key, str(value)) for key, value in sorted(query.items()) if value is not None
            ]
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
                method,
                request_path,
                params,
                payload.encode() if method.upper() != "GET" else None,
                signed,
            )
            response = NativeResponse(
                status,
                dict(response_headers),
                bytes(response_body),
            )

        except RuntimeError as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=resp_headers,
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
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                ) from exc

            if data.get("retCode", 0) != 0:
                code = data.get("retCode", "Unknown")
                error_message = data.get("retMsg", "Unknown error")
                self._log_failed_request(f"Bybit API Error: [{code}] {error_message}", code)
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Bybit API Error: [{code}] {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data
