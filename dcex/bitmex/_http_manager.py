"""
BitMEX HTTP Manager for API communication.

This module provides the core HTTP management functionality for communicating
with the BitMEX API, including authentication, request signing, rate limiting,
and error handling.
"""

import hashlib
import hmac
import logging
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import msgspec
import requests

from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    BitMEX HTTP Manager for API communication.

    This class handles all HTTP communication with the BitMEX API, including
    authentication, request signing, rate limiting, and error handling.
    It provides a base class for all BitMEX API operations.

    Attributes:
        base_url: Base URL for the BitMEX API
        api_key: API key for authentication
        api_secret: API secret for request signing
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
        session: HTTP session for connection pooling
        ptm: Product table manager for symbol conversion
        preload_product_table: Whether to preload product table on initialization
    """

    EXCHANGE = Common.BITMEX

    base_url: str = "https://www.bitmex.com"
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logging and optionally
        preloads the product table for symbol conversion.
        """
        self._logger = self._setup_logger(self.logger)

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BITMEX)

    def _sign(self, method: str, path: str, expires: int, body: str = "") -> str:
        """
        Generate BitMEX API signature according to BitMEX documentation.

        Creates a HMAC-SHA256 signature for authenticating API requests.
        The signature is generated using the API secret and includes the
        HTTP method, path, expiration timestamp, and request body.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            expires: Unix timestamp when the request expires
            body: Request body content (empty string for GET requests)

        Returns:
            Hex-encoded HMAC-SHA256 signature

        Raises:
            ValueError: If api_secret is not configured
        """
        if self.api_secret is None:
            raise ValueError("api_secret is required for signing requests")
        message = method + path + str(expires) + body
        signature = hmac.new(
            self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def _headers(
        self, method: str, path: str, body: str = "", signed: bool = True
    ) -> dict[str, str]:
        """
        Generate headers for BitMEX API requests.

        Creates the necessary HTTP headers for API requests, including
        authentication headers when signing is enabled.

        Args:
            method: HTTP method for the request
            path: API endpoint path
            body: Request body content
            signed: Whether to include authentication headers

        Returns:
            Dictionary containing HTTP headers
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.api_key and self.api_secret and signed:
            expires = int(time.time()) + 5  # 5 seconds from now
            signature = self._sign(method, path, expires, body)
            headers.update(
                {"api-key": self.api_key, "api-signature": signature, "api-expires": str(expires)}
            )

        return headers

    def _request(
        self,
        method: str,
        path: str,
        query: Mapping[str, str | int | Sequence[str | int] | float | bool] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the BitMEX API.

        Handles all HTTP methods (GET, POST, PUT, DELETE) with proper
        authentication, error handling, and response header tracking.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            query: Query parameters or request body data
            signed: Whether to sign the request with authentication

        Returns:
            Dictionary containing the API response data

        Raises:
            FailedRequestError: If the API request fails or returns an error
            ValueError: If an unsupported HTTP method is used
        """
        if self.session is None:
            raise RuntimeError("HTTP session is not initialized")

        response = None
        try:
            url = f"{self.base_url}{path}"
            body = ""
            full_path = path
            self._log_request(method, url)

            if method.upper() == "GET":
                if query:
                    query_string = urlencode(query)
                    url += f"?{query_string}"
                    full_path += f"?{query_string}"
                response = self.session.get(
                    url,
                    headers=self._headers(method, full_path, signed=signed),
                    timeout=self.timeout,
                )
            elif method.upper() == "POST":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = self.session.post(
                    url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    data=body,
                    timeout=self.timeout,
                )
            elif method.upper() == "PUT":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = self.session.put(
                    url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    data=body,
                    timeout=self.timeout,
                )
            elif method.upper() == "DELETE":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = self.session.request(
                    method="DELETE",
                    url=url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    data=body,
                    timeout=self.timeout,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                ) from exc

            timestamp = str(generate_timestamp(iso_format=True))

            if not response.status_code // 100 == 2:
                error_message = (
                    data.get("error", {}).get("message", "Unknown error")
                    if isinstance(data, dict)
                    else response.text
                )
                self._log_failed_request(f"BITMEX API Error: {error_message}", response.status_code)
                raise FailedRequestError(
                    request=f"{method} {url} | Body: {query}",
                    message=f"BITMEX API Error: {error_message}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                )
            else:
                return data

        except requests.exceptions.RequestException as e:
            timestamp = str(generate_timestamp(iso_format=True))
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=timestamp,
                resp_headers=resp_headers,
            ) from e

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
