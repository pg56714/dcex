"""
Gate.io HTTP Manager for API communication.

This module provides the base HTTP manager class for all Gate.io API operations,
handling authentication, request signing, and error management.
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import msgspec
import requests

from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError


@dataclass
class HTTPManager:
    """
    Base HTTP manager for Gate.io API operations.

    This class provides the foundation for all Gate.io API clients, handling:
    - API authentication and request signing
    - HTTP request/response management
    - Error handling and logging
    - Product table management

    Attributes:
        api_key: Gate.io API key for authentication
        api_secret: Gate.io API secret for request signing
        base_url: Base URL for the Gate.io API
        logger: Logger instance for debugging
        session: HTTP session for connection pooling
        preload_product_table: Whether to preload product table on initialization
    """

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    base_url: str = field(default="https://api.gateio.ws")
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    preload_product_table: bool = field(default=True)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logging and preloads the product table if configured.
        """
        if self.logger is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = self.logger

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.GATEIO)

    def _resolve_path(
        self, path_template: str | Enum, path_params: dict[str, Any] | None = None
    ) -> str:
        """
        Resolve path template with parameters.

        Args:
            path_template: Path template string or Enum
            path_params: Dictionary of parameters to substitute in the template

        Returns:
            str: Resolved path string

        Raises:
            ValueError: If required path parameters are missing
        """
        if isinstance(path_template, Enum):
            path_template = path_template.value

        try:
            return str(path_template).format(**(path_params or {}))
        except KeyError as e:
            raise ValueError(f"Missing path parameter: {e}") from e

    def _sign(
        self,
        method: str,
        url_path: str,
        query: dict[str, Any] | None,
        body: dict[str, Any] | list | None,
        timestamp: str,
    ) -> str:
        """
        Generate HMAC-SHA512 signature for API request authentication.

        Args:
            method: HTTP method (GET, POST, etc.)
            url_path: API endpoint path
            query: Query parameters dictionary
            body: Request body data
            timestamp: Request timestamp string

        Returns:
            str: HMAC-SHA512 signature hex string

        Raises:
            ValueError: If API secret is not configured
        """
        if not self.api_secret:
            raise ValueError("API secret is required for signing")

        payload_string = msgspec.json.encode(body or {}).decode("utf-8") if body else ""
        hashed_payload = hashlib.sha512(payload_string.encode("utf-8")).hexdigest()

        query_string = ""
        if query:
            query_string = "&".join(f"{k}={v}" for k, v in sorted(query.items()))

        s = f"{method.upper()}\n{url_path}\n{query_string}\n{hashed_payload}\n{timestamp}"
        return hmac.new(
            self.api_secret.encode("utf-8"), s.encode("utf-8"), hashlib.sha512
        ).hexdigest()

    def _request(
        self,
        method: str,
        path: str | Enum,
        path_params: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | list | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Gate.io API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            path: API endpoint path or Enum
            path_params: Parameters to substitute in the path template
            query: Query parameters
            body: Request body data
            signed: Whether to sign the request with API credentials

        Returns:
            dict[str, Any]: API response data

        Raises:
            ValueError: If API credentials are missing for signed requests
            FailedRequestError: If the API request fails
        """
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
                response = self.session.get(url, headers=headers, params=query)
            elif method_upper == "POST":
                if body:
                    response = self.session.post(
                        url, headers=headers, params=query, data=body_string
                    )
                else:
                    response = self.session.post(url, headers=headers, params=query)
            elif method_upper == "PUT":
                response = self.session.put(url, headers=headers, params=query, data=body_string)
            elif method_upper == "DELETE":
                response = self.session.delete(url, headers=headers, params=query)
            elif method_upper == "PATCH":
                response = self.session.patch(url, headers=headers, params=query, data=body_string)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.ok:
                return response.json()

            raise FailedRequestError(
                request=f"{method_upper} {url}",
                message=f"GATEIO API Error: {response.status_code}, {response.text}",
                status_code=response.status_code,
                time=timestamp,
                resp_headers=dict(response.headers),
            )

        except FailedRequestError:
            raise
        except Exception as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url}",
                message=f"Request failed: {e}",
                status_code="unknown",
                time=timestamp,
                resp_headers={},
            ) from e
