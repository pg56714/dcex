"""
Gate.io HTTP manager module.

This module provides the HTTPManager class for handling HTTP requests
to the Gate.io API, including authentication, request signing, and
response handling.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Self, cast

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
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
        ptm: Product table manager
        preload_product_table: Whether to preload product table
    """

    EXCHANGE = Common.GATEIO

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    base_url: str = field(default="https://api.gateio.ws")
    logger: logging.Logger | None = field(default=None)
    timeout: int = field(default=10)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Returns:
            Self instance for method chaining
        """
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.GATEIO)
        native_client_type = getattr(_native, "GateioHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if (
            self.preload_product_table
            and self._native_client is not None
            and hasattr(self._native_client, "set_product_table")
        ):
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
        """Call a Rust-backed Gate.io private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Gate.io native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_async"):
            raise RuntimeError("Gate.io native client private_request_async is unavailable.")
        try:
            status, headers, body = await self._native_client.private_request_async(
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

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        path: str,
        path_params: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | list | None = None,
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
            RuntimeError: If native initialization fails
            ValueError: If signed request lacks credentials
            FailedRequestError: If request fails or API returns error
        """
        if self._native_client is None:
            await self.async_init()

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
            if method_upper in ("POST", "PUT", "PATCH") and body:
                body_string = json.dumps(body, separators=(",", ":"))

            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
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

        except FailedRequestError:
            raise
        except Exception as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method_upper} {url}",
                message=f"Request failed: {e}",
                status_code=status_code,
                time=timestamp,
                resp_headers=resp_headers,
            ) from e
        else:
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

            if response.status_code // 100 == 2:
                return data

            self._log_failed_request(f"GATEIO API Error: {response.text}", response.status_code)
            raise FailedRequestError(
                request=f"{method_upper} {url}",
                message=f"GATEIO API Error: {response.status_code}, {response.text}",
                status_code=response.status_code,
                time=timestamp,
                resp_headers=dict(response.headers),
            )
