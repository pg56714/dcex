"""
Gate.io HTTP Manager for API communication.

This module provides the base HTTP manager class for all Gate.io API operations,
handling authentication, request signing, and error management.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast

from .._native_http import NativeResponse, load_native, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
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
        timeout: Request timeout in seconds
        preload_product_table: Whether to preload product table on initialization
    """

    EXCHANGE = Common.GATEIO

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    base_url: str = field(default="https://api.gateio.ws")
    logger: logging.Logger | None = field(default=None)
    timeout: int = field(default=10)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logging and preloads the product table if configured.
        """
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "GateioHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        self._native_client = native_client_type(
            api_key=self.api_key,
            api_secret=self.api_secret,
            timeout=self.timeout,
            base_url=self.base_url,
        )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.GATEIO)
            if self._native_client is not None and hasattr(
                self._native_client, "set_product_table"
            ):
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Gate.io private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Gate.io native client is required for private methods.")
        if not hasattr(self._native_client, "private_request"):
            raise RuntimeError("Gate.io native client private_request is unavailable.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Gate.io {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if key in {"type_", "from_"}:
                key = key[:-1]
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict, tuple)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

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

        timestamp = str(generate_timestamp(iso_format=True))
        self._uses_native_transport()

        if signed:
            if not (self.api_key and self.api_secret):
                raise ValueError("Signed request requires API Key and Secret.")

        self._log_request(method, url)

        try:
            method_upper = method.upper()
            body_string = None
            if method_upper in ("POST", "PUT", "PATCH"):
                body_string = json.dumps(body, separators=(",", ":"))

            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw(
                method,
                full_path,
                [(key, str(value)) for key, value in query.items()],
                body_string.encode() if body_string and body else None,
                signed,
            )
            response = NativeResponse(
                status,
                dict(response_headers),
                bytes(response_body),
            )

            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method_upper} {url}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                ) from exc

            if response.ok:
                return data

            self._log_failed_request(f"GATEIO API Error: {response.text}", response.status_code)
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
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url}",
                message=f"Request failed: {e}",
                status_code=status_code,
                time=timestamp,
                resp_headers=resp_headers,
            ) from e

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
