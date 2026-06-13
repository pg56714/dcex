"""
Bybit HTTP manager module.

This module provides the HTTPManager class for handling HTTP requests
to the Bybit API, including authentication, request signing, and
response handling.
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Self

import httpx
import msgspec

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
TIME_ENDPOINT = "/v5/market/time"


def _extract_server_time_ms(data: dict[str, Any]) -> int | None:
    value = data.get("time")
    if value is not None:
        return int(value)

    result = data.get("result")
    if isinstance(result, dict):
        time_nano = result.get("timeNano")
        if time_nano is not None:
            return int(time_nano) // 1_000_000

        time_second = result.get("timeSecond")
        if time_second is not None:
            return int(time_second) * 1_000

    return None


def get_header(api_key: str, signature: str, timestamp: int, recv_window: int) -> dict[str, str]:
    """
    Generate authentication headers for signed requests.

    Args:
        api_key: API key
        signature: Request signature
        timestamp: Request timestamp
        recv_window: Receive window

    Returns:
        Dict containing authentication headers
    """
    return {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-SIGN-TYPE": "2",
        "X-BAPI-TIMESTAMP": str(timestamp),
        "X-BAPI-RECV-WINDOW": str(recv_window),
    }


def get_header_no_sign() -> dict[str, str]:
    """
    Generate headers for unsigned requests.

    Returns:
        Dict containing basic headers
    """
    return {"Content-Type": "application/json"}


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
        session: HTTP client session
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
    session: httpx.AsyncClient | None = field(init=False, default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    sync_server_time: bool = field(default=True)
    timestamp_offset_ms: int = field(default=0, repr=False)
    _time_offset_synced: bool = field(default=False, init=False, repr=False)

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
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def _sync_time_offset(self) -> None:
        if self._time_offset_synced or not self.sync_server_time:
            self._time_offset_synced = True
            return

        self._time_offset_synced = True
        if self.session is None:
            return

        try:
            local_start = int(generate_timestamp())
            response = await self.session.get(
                self.endpoint + TIME_ENDPOINT,
                headers=get_header_no_sign(),
                timeout=self.timeout,
            )
            local_end = int(generate_timestamp())
            data = response.json()
            server_time_ms = _extract_server_time_ms(data)
            if response.status_code // 100 == 2 and server_time_ms is not None:
                self.timestamp_offset_ms = server_time_ms - ((local_start + local_end) // 2)
        except Exception:
            return

    async def _timestamp(self, signed: bool) -> int:
        # Bybit rejects signed requests more than 1000ms ahead of server time.
        if signed:
            await self._sync_time_offset()
        return int(generate_timestamp()) + self.timestamp_offset_ms

    def _auth(self, payload: str, timestamp: int) -> str:
        """
        Generate authentication signature.

        Args:
            payload: Request payload string
            timestamp: Request timestamp

        Returns:
            HMAC-SHA256 signature

        Raises:
            ValueError: If api_secret is not set
        """
        if self.api_secret is None:
            raise ValueError("api_secret is required for signing requests")
        param_str = f"{timestamp}{self.api_key}{self.recv_window}{payload}"
        return hmac.new(self.api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()

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
            RuntimeError: If session initialization fails
            ValueError: If signed request lacks credentials
            FailedRequestError: If request fails or API returns error
        """
        if self.session is None or self.session.is_closed:
            await self.async_init()

        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session")

        if query is None:
            query = {}

        timestamp = await self._timestamp(signed)

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
            payload = msgspec.json.encode(query).decode("utf-8")

        if signed:
            if not (self.api_key and self.api_secret):
                raise ValueError("Signed request requires API Key and Secret.")
            signature = self._auth(payload, timestamp)
            headers = get_header(self.api_key, signature, timestamp, self.recv_window)
        else:
            headers = get_header_no_sign()

        url = self.endpoint + path
        self._log_request(method, url)
        response = None

        try:
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.session.post(url, headers=headers, content=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except httpx.HTTPError as e:
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
