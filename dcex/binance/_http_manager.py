import json
import logging
from dataclasses import dataclass, field
from typing import Any, cast

from .._native_http import load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    HTTP manager for Binance API requests.

    Handles authentication, request signing, and API endpoint routing for both
    spot and futures trading APIs.
    """

    EXCHANGE = Common.BINANCE

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the HTTP manager after dataclass creation."""
        self._logger = self._setup_logger(self.logger)

        self._native_client = _native.BinanceHttpClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            timeout=self.timeout,
        )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BINANCE)
            if self._native_client is not None:
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _request(
        self,
        method: str,
        path: str,
        query: dict | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Binance API.

        Args:
            method: HTTP method (GET, POST, DELETE).
            path: API endpoint path enum.
            query: Query parameters for the request.
            signed: Whether to sign the request with API credentials.

        Returns:
            dict[str, Any]: Response data from the API.

        Raises:
            ValueError: If API credentials are required but not provided.
            FailedRequestError: If the API request fails or returns an error.
        """
        query = dict(query or {})
        if signed and not (self.api_key and self.api_secret):
            raise ValueError("Signed request requires API Key and Secret.")

        request_path = str(path)
        url = request_path
        self._log_request(method, url)
        self._uses_native_transport()
        native_client = cast(Any, self._native_client)
        try:
            status_code, response_headers, body = native_client.request_raw_auto(
                method,
                request_path,
                [(str(key), str(value)) for key, value in query.items()],
                signed,
            )
            response_headers = dict(response_headers)
            response_text = bytes(body).decode(errors="replace")
            self.last_response_headers = response_headers
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(exc)}",
                status_code=status_code,
                time=query.get("timestamp", "Unknown"),
                resp_headers=resp_headers,
            ) from exc

        try:
            data = json.loads(body)
        except Exception as exc:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Failed to decode JSON response: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=response_headers,
            ) from exc

        timestamp = generate_timestamp(iso_format=True)
        if isinstance(data, dict) and "code" in data and str(data["code"]) != "200":
            code = data.get("code", "Unknown")
            error_message = data.get("msg", "Unknown error")
            self._log_failed_request(f"BINANCE API Error: [{code}] {error_message}", code)
            raise FailedRequestError(
                request=f"{method} {url} | Body: {query}",
                message=f"BINANCE API Error: [{code}] {error_message}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=response_headers,
            )

        if not status_code // 100 == 2:
            self._log_failed_request(
                f"HTTP Error {status_code}: {response_text}",
                status_code,
            )
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"HTTP Error {status_code}: {response_text}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=response_headers,
            )
        return data

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
