import json
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast

from ..._native_http import NativeResponse, load_native, native_body_text, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


def _query_pairs(
    query: Mapping[str, str | int | Sequence[str | int] | float | bool] | None,
) -> list[tuple[str, str]]:
    if not query:
        return []
    params: list[tuple[str, str]] = []
    for key, value in query.items():
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            params.extend((key, str(item)) for item in value)
        else:
            params.append((key, str(value)))
    return params


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    Base HTTP manager for BitMEX API interactions.

    This class provides the foundation for all BitMEX API HTTP clients,
    handling authentication, request signing, error handling, and response
    header tracking through the Rust native transport.

    Attributes:
        base_url: Base URL for BitMEX API
        api_key: API key for authentication
        api_secret: API secret for request signing
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
    """

    EXCHANGE = Common.BITMEX

    base_url: str = "https://www.bitmex.com"
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Initializes native transport state and optionally loads the product table manager.

        Returns:
            HTTPManager: Self instance for method chaining

        Raises:
            RuntimeError: If native initialization fails
        """
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITMEX)
        native_client_type = getattr(_native, "BitmexHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
                base_url=self.base_url,
            )
            if self.preload_product_table and hasattr(native_client, "set_product_table"):
                native_client.set_product_table(self.ptm._native_table)
            self._native_client = native_client
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _require_credentials(self) -> None:
        """Validate credentials before entering a signed BitMEX request path."""
        if not (self.api_key and self.api_secret):
            raise ValueError("Signed request requires API Key and Secret.")

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BitMEX private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMEX native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_json_async"):
            raise RuntimeError("BitMEX native client private_request_json_async is unavailable.")
        self._require_credentials()
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BITMEX {method_name} | Params: {params}",
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
            if isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: Mapping[str, str | int | Sequence[str | int] | float | bool] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the BitMEX API.

        Handles request preparation, execution, response parsing, and error handling.
        Automatically initializes native transport if needed and stores response headers.

        Args:
            method: HTTP method to use
            path: API endpoint path
            query: Query parameters or request body data
            signed: Whether to sign the request with authentication

        Returns:
            dict[str, Any]: Parsed JSON response data

        Raises:
            RuntimeError: If native initialization fails
            ValueError: If unsupported HTTP method is used
            FailedRequestError: If API request fails or returns error
        """
        if self._native_client is None:
            await self.async_init()
        try:
            url = f"{self.base_url}{path}"
            method_upper = method.upper()
            if method_upper not in {"GET", "POST", "PUT", "DELETE"}:
                raise ValueError(f"Unsupported method: {method}")
            self._log_request(method, url)

            self._uses_native_transport()
            if signed:
                self._require_credentials()
            params = _query_pairs(query) if method_upper == "GET" else []
            body_bytes = (
                json.dumps(query, separators=(",", ":")).encode()
                if query and method_upper != "GET"
                else None
            )
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_json_async(
                method,
                path,
                params,
                body_bytes,
                signed,
            )
            response = NativeResponse(status, dict(response_headers))

        except RuntimeError as e:
            timestamp = generate_timestamp(iso_format=True)
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=resp_headers,
            ) from e
        else:
            self._store_response_headers(response)
            data = response_body
            timestamp = generate_timestamp(iso_format=True)

            if not response.status_code // 100 == 2:
                error_message = (
                    data.get("error", {}).get("message", "Unknown error")
                    if isinstance(data, dict)
                    else native_body_text(data)
                )
                self._log_failed_request(f"BITMEX API Error: {error_message}", response.status_code)
                raise FailedRequestError(
                    request=f"{method} {url} | Body: {query}",
                    message=f"BITMEX API Error: {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data
