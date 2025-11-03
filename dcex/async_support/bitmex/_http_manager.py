import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal, Self
from urllib.parse import urlencode

import httpx
import msgspec

from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


@dataclass
class HTTPManager:
    """
    Base HTTP manager for BitMEX API interactions.

    This class provides the foundation for all BitMEX API HTTP clients,
    handling authentication, request signing, session management, and
    error handling. It includes optimized TCP settings and rate limiting
    information tracking.

    Attributes:
        base_url: Base URL for BitMEX API
        api_key: API key for authentication
        api_secret: API secret for request signing
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
        session: HTTP client session
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
        last_rate_limit_info: Last received rate limit information
    """

    base_url: str = "https://www.bitmex.com"
    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    timeout: int = field(default=5)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(init=False, default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    last_rate_limit_info: dict[str, Any] | None = field(default=None, init=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Sets up the HTTP client session with optimized TCP settings,
        and optionally loads the product table manager.

        Returns:
            HTTPManager: Self instance for method chaining

        Raises:
            RuntimeError: If session initialization fails
        """
        self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self.logger or logging.getLogger(__name__)
        self.last_rate_limit_info = None
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITMEX)
        return self

    def _sign(self, method: str, path: str, expires: int, body: str = "") -> str:
        """
        Generate BitMEX API signature for request authentication.

        Creates HMAC-SHA256 signature according to BitMEX documentation.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            expires: Expiration timestamp
            body: Request body content

        Returns:
            str: Base64-encoded signature

        Raises:
            ValueError: If api_secret is not provided
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
        Generate HTTP headers for BitMEX API requests.

        Creates standard headers and optionally adds authentication headers
        with API key, signature, and expiration timestamp.

        Args:
            method: HTTP method
            path: API endpoint path
            body: Request body content
            signed: Whether to include authentication headers

        Returns:
            dict[str, str]: HTTP headers dictionary
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.api_key and self.api_secret and signed:
            expires = int(time.time()) + 5  # 5 seconds from now
            signature = self._sign(method, path, expires, body)
            headers.update(
                {"api-key": self.api_key, "api-signature": signature, "api-expires": str(expires)}
            )

        return headers

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, str | int | list[str] | float | bool] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the BitMEX API.

        Handles request preparation, execution, response parsing, and error handling.
        Automatically initializes session if needed and updates rate limit information.

        Args:
            method: HTTP method to use
            path: API endpoint path
            query: Query parameters or request body data
            signed: Whether to sign the request with authentication

        Returns:
            dict[str, Any]: Parsed JSON response data

        Raises:
            RuntimeError: If session initialization fails
            ValueError: If unsupported HTTP method is used
            FailedRequestError: If API request fails or returns error
        """
        if self.session is None or self.session.is_closed:
            await self.async_init()

        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session")

        response = None
        try:
            url = f"{self.base_url}{path}"
            body = ""
            full_path = path

            if method.upper() == "GET":
                if query:
                    query_string = urlencode(query)
                    url += f"?{query_string}"
                    full_path += f"?{query_string}"
                response = await self.session.get(
                    url, headers=self._headers(method, full_path, signed=signed)
                )
            elif method.upper() == "POST":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = await self.session.post(
                    url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    content=body,
                )
            elif method.upper() == "PUT":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = await self.session.put(
                    url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    content=body,
                )
            elif method.upper() == "DELETE":
                body = msgspec.json.encode(query).decode("utf-8") if query else ""
                response = await self.session.request(
                    method="DELETE",
                    url=url,
                    headers=self._headers(method, full_path, body, signed=signed),
                    content=body,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

        except httpx.RequestError as e:
            timestamp = generate_timestamp(iso_format=True)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(e)}",
                status_code=response.status_code if response else "Unknown",
                time=str(timestamp),
                resp_headers=dict(response.headers) if response else None,
            ) from e
        else:
            try:
                data = response.json()
            except Exception:
                data = {}

            timestamp = generate_timestamp(iso_format=True)

            if not response.status_code // 100 == 2:
                error_message = (
                    data.get("error", {}).get("message", "Unknown error")
                    if isinstance(data, dict)
                    else response.text
                )
                raise FailedRequestError(
                    request=f"{method} {url} | Body: {query}",
                    message=f"BITMEX API Error: {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            self._update_rate_limit_info(response.headers)

            return data

    def _update_rate_limit_info(self, headers: httpx.Headers) -> None:
        """
        Update rate limit information from response headers.

        Extracts rate limiting information from BitMEX API response headers
        and stores it for monitoring and debugging purposes.

        Args:
            headers: HTTP response headers
        """
        if "x-ratelimit-remaining" in headers:
            self.last_rate_limit_info = {
                "limit": headers.get("x-ratelimit-limit"),
                "remaining": headers.get("x-ratelimit-remaining"),
                "reset": headers.get("x-ratelimit-reset"),
                "remaining-1s": headers.get("x-ratelimit-remaining-1s"),
            }

    def get_rate_limit_info(self) -> dict[str, Any] | None:
        """
        Get the last received rate limit information.

        Returns:
            dict[str, Any] | None: Rate limit information including limit,
                remaining requests, reset time, and per-second limits
        """
        return self.last_rate_limit_info
