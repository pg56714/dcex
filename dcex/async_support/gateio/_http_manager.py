"""
Gate.io HTTP manager module.

This module provides the HTTPManager class for handling HTTP requests
to the Gate.io API, including authentication, request signing, and
response handling.
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Self

import httpx
import msgspec

from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ..product_table.manager import ProductTableManager


@dataclass
class HTTPManager:
    """
    HTTP manager for Gate.io API requests.

    This class handles HTTP requests to the Gate.io API, including:
    - Authentication and request signing
    - Error handling
    - Product table management
    - Session management

    Attributes:
        api_key: API key for authentication
        api_secret: API secret for signing
        base_url: Base URL for API requests
        logger: Logger instance
        timeout: Request timeout in seconds
        session: HTTP client session
        ptm: Product table manager
        preload_product_table: Whether to preload product table
    """

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    base_url: str = field(default="https://api.gateio.ws")
    logger: logging.Logger | None = field(default=None)
    timeout: int = field(default=10)
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Returns:
            Self instance for method chaining
        """
        self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self.logger or logging.getLogger(__name__)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.GATEIO)
        return self

    def _resolve_path(
        self, path_template: str | Enum, path_params: dict[str, Any] | None = None
    ) -> str:
        """
        Resolve path template with parameters.

        Args:
            path_template: Path template string or Enum
            path_params: Optional path parameters

        Returns:
            Resolved path string

        Raises:
            ValueError: If required path parameters are missing
        """
        if isinstance(path_template, Enum):
            path_template = str(path_template.value)
        try:
            return path_template.format(**(path_params or {}))
        except KeyError as e:
            raise ValueError(f"Missing path parameter: {e}") from e

    def _sign(
        self,
        method: str,
        url_path: str,
        query: dict[str, Any] | None,
        body: dict[str, Any] | None,
        timestamp: str,
    ) -> str:
        """
        Generate authentication signature.

        Args:
            method: HTTP method
            url_path: URL path
            query: Query parameters
            body: Request body
            timestamp: Request timestamp

        Returns:
            HMAC-SHA512 signature

        Raises:
            ValueError: If API secret is not set
        """
        payload_string = msgspec.json.encode(body or {}).decode("utf-8") if body else ""
        hashed_payload = hashlib.sha512(payload_string.encode("utf-8")).hexdigest()

        query_string = ""
        if query:
            query_string = "&".join(f"{k}={v}" for k, v in sorted(query.items()))

        s = f"{method.upper()}\n{url_path}\n{query_string}\n{hashed_payload}\n{timestamp}"
        if self.api_secret is None:
            raise ValueError("API secret is required for signing")
        return hmac.new(
            self.api_secret.encode("utf-8"), s.encode("utf-8"), hashlib.sha512
        ).hexdigest()

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        path: str,
        path_params: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to Gate.io API.

        Args:
            method: HTTP method
            path: API endpoint path
            path_params: Optional path parameters
            query: Optional query parameters
            body: Optional request body
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

        query = query or {}
        body = body or {}

        resolved_path = self._resolve_path(path, path_params)
        full_path = "/api/v4" + resolved_path
        url = self.base_url + full_path

        timestamp = str(int(time.time()))
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if signed:
            if not (self.api_key and self.api_secret):
                raise ValueError("Signed request requires API Key and Secret.")
            sign = self._sign(method, full_path, query, body, timestamp)
            headers.update(
                {
                    "KEY": self.api_key,
                    "Timestamp": timestamp,
                    "SIGN": sign,
                }
            )

        try:
            method_upper = method.upper()
            body_string = None
            if method_upper in ("POST", "PUT", "PATCH"):
                body_string = msgspec.json.encode(body).decode("utf-8")

            if method_upper == "GET":
                response = await self.session.get(url, headers=headers, params=query)
            elif method_upper == "POST":
                response = await self.session.post(
                    url, headers=headers, params=query, content=body_string
                )
            elif method_upper == "PUT":
                response = await self.session.put(
                    url, headers=headers, params=query, content=body_string
                )
            elif method_upper == "DELETE":
                response = await self.session.delete(url, headers=headers, params=query)
            elif method_upper == "PATCH":
                response = await self.session.patch(
                    url, headers=headers, params=query, content=body_string
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except FailedRequestError:
            raise
        except Exception as e:
            raise FailedRequestError(
                request=f"{method_upper} {url}",
                message=f"Request failed: {e}",
                status_code="unknown",
                time=timestamp,
                resp_headers={},
            ) from e
        else:
            if response.status_code // 100 == 2:
                return response.json()

            raise FailedRequestError(
                request=f"{method_upper} {url}",
                message=f"GATEIO API Error: {response.status_code}, {response.text}",
                status_code=response.status_code,
                time=timestamp,
                resp_headers=dict(response.headers),
            )
