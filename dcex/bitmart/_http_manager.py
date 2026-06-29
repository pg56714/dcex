"""Bitmart HTTP manager for handling API requests and authentication."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, cast

from .._native_http import NativeResponse, load_native, native_body_text, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    HTTP manager for Bitmart API requests.

    This class handles authentication, request signing, and API communication
    for both spot and futures trading endpoints.
    """

    EXCHANGE = Common.BITMART

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    memo: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize logger and product table manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "BitmartHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        self._native_client = native_client_type(
            api_key=self.api_key,
            api_secret=self.api_secret,
            memo=self.memo,
            timeout=self.timeout,
        )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BITMART)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
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
        """Call a Rust-backed BitMart private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMart native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_json"):
            raise RuntimeError("BitMart native client private_request_json is unavailable.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BITMART {method_name} | Params: {params}",
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
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to Bitmart API.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path
            query: Request parameters
            signed: Whether to sign the request

        Returns:
            API response data

        Raises:
            ValueError: If API credentials are missing for signed requests
            FailedRequestError: If the API request fails
        """
        if query is None:
            query = {}

        request_path = str(path)
        url = request_path

        method_upper = method.upper()
        if method_upper == "GET" and query:
            params_str = "&".join(
                f"{k}={str(v).lower() if isinstance(v, bool) else v}"
                for k, v in sorted(query.items())
                if v is not None
            )
            url = f"{url}?{params_str}"

        timestamp = generate_timestamp()
        body = (
            json.dumps(query if query else {}, separators=(",", ":"))
            if method_upper == "POST"
            else ""
        )

        if signed and not (self.api_key and self.api_secret and self.memo):
            raise ValueError("Signed request requires API Key and Secret and Memo.")

        self._log_request(method, url)

        try:
            self._uses_native_transport()
            params = [
                (
                    key,
                    str(value).lower() if isinstance(value, bool) else str(value),
                )
                for key, value in sorted(query.items())
                if value is not None
            ]
            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw_auto_json(
                method,
                request_path,
                params,
                body.encode() if method_upper == "POST" else None,
                signed,
            )
            response = NativeResponse(status, dict(response_headers))

            self._store_response_headers(response)
            data = response_body
            if data.get("code", 0) != 1000:
                code = data.get("code", "Unknown")
                error_msg = data.get("msg") or data.get("message") or "Unknown error"
                self._log_failed_request(f"BitMart API Error: [{code}] {error_msg}", code)
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"BitMart API Error: [{code}] {error_msg}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            # If http status is not 2xx (like 403, 404)
            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {native_body_text(data)}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )
            else:
                return data

        except RuntimeError as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=resp_headers,
            ) from e

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
