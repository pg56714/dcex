"""
Bybit HTTP Manager.

This module provides the base HTTP client functionality for all Bybit API
operations, including authentication, request handling, and error management.
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any

import msgspec
import requests

from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

HTTP_URL = "https://{SUBDOMAIN}.{DOMAIN}.{TLD}"
SUBDOMAIN_TESTNET = "api-testnet"
SUBDOMAIN_MAINNET = "api"
DOMAIN_MAIN = "bybit"
TLD_MAIN = "com"


def get_header(api_key: str, signature: str, timestamp: int, recv_window: int) -> dict[str, str]:
    """
    Generate authentication headers for signed requests.

    Args:
        api_key: API key
        signature: Request signature
        timestamp: Request timestamp
        recv_window: Receive window

    Returns:
        dict[str, str]: Authentication headers
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
        dict[str, str]: Basic headers without authentication
    """
    return {"Content-Type": "application/json"}


@dataclass
class HTTPManager:
    """
    Base HTTP manager for Bybit API operations.

    This class provides the foundation for all HTTP-based API operations
    including authentication, request handling, error management, and
    product table integration.

    Attributes:
        testnet: Whether to use testnet environment
        domain: API domain
        tld: Top-level domain
        api_key: API key for authentication
        api_secret: API secret for authentication
        timeout: Request timeout in seconds
        recv_window: Receive window for requests
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        logger: Logger instance
        session: HTTP session for connection pooling
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
    """

    testnet: bool = field(default=False)
    domain: str = field(default=DOMAIN_MAIN)
    tld: str = field(default=TLD_MAIN)
    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    timeout: int = field(default=10)
    recv_window: int = field(default=5000)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logging, endpoint URL, and product table manager.
        """
        if self.logger is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = self.logger

        subdomain = SUBDOMAIN_TESTNET if self.testnet else SUBDOMAIN_MAINNET
        self.endpoint = HTTP_URL.format(SUBDOMAIN=subdomain, DOMAIN=self.domain, TLD=self.tld)

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BYBIT)

    def _auth(self, payload: str, timestamp: int) -> str:
        """
        Generate authentication signature.

        Args:
            payload: Request payload string
            timestamp: Request timestamp

        Returns:
            str: HMAC-SHA256 signature

        Raises:
            ValueError: If API secret is not provided
        """
        if not self.api_secret:
            raise ValueError("API secret is required for authentication")
        param_str = f"{timestamp}{self.api_key}{self.recv_window}{payload}"
        return hmac.new(self.api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Bybit API.

        Args:
            method: HTTP method ("GET" or "POST")
            path: API endpoint path
            query: Query parameters or request body
            signed: Whether to sign the request

        Returns:
            dict[str, Any]: API response data

        Raises:
            ValueError: If API credentials are missing for signed requests
            FailedRequestError: If the request fails or returns an error
        """
        if query is None:
            query = {}

        timestamp = generate_timestamp()
        if not isinstance(timestamp, int):
            raise TypeError("Expected integer timestamp")

        if method.upper() == "GET":
            if query:
                sorted_query = "&".join(f"{k}={v}" for k, v in sorted(query.items()) if v)
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

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(
                    url, data=payload, headers=headers, timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            try:
                data = response.json()
            except Exception:
                data = {}

            if data.get("retCode", 0) != 0:
                code = data.get("retCode", "Unknown")
                error_message = data.get("retMsg", "Unknown error")
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Bybit API Error: [{code}] {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )
            elif not response.status_code // 100 == 2:
                # If http status is not 2xx (like 403, 404)
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )
            else:
                return data

        except requests.exceptions.RequestException as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {payload}",
                message=f"Request failed: {str(e)}",
                status_code=getattr(e.response, "status_code", "Unknown"),
                time=str(timestamp),
                resp_headers=getattr(e.response, "headers", None),
            ) from e
