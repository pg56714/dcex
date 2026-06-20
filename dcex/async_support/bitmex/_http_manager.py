import hashlib
import hmac
import json
import logging
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import parse_qsl, urlencode

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
    Base HTTP manager for BitMEX API interactions.

    This class provides the foundation for all BitMEX API HTTP clients,
    handling authentication, request signing, session management, and
    error handling. It includes optimized TCP settings and response
    header tracking.

    Attributes:
        base_url: Base URL for BitMEX API
        api_key: API key for authentication
        api_secret: API secret for request signing
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
        session: HTTP client session
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
    """

    EXCHANGE = Common.BITMEX

    base_url: str = "https://www.bitmex.com"
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: Any = field(default=None, init=False, repr=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

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
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITMEX)
        native_client_type = getattr(_native, "BitmexHttpClient", None)
        if self.use_native and native_client_type is not None and self._native_client is None:
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
        if not self.use_native or self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BitMEX private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMEX native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_async"):
            raise RuntimeError("BitMEX native client private_request_async is unavailable.")
        try:
            status, headers, body = await self._native_client.private_request_async(
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
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

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
        query: Mapping[str, str | int | Sequence[str | int] | float | bool] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the BitMEX API.

        Handles request preparation, execution, response parsing, and error handling.
        Automatically initializes session if needed and stores response headers.

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
        if self._native_client is None:
            await self.async_init()

        response = None
        try:
            url = f"{self.base_url}{path}"
            body = ""
            full_path = path
            self._log_request(method, url)

            if self._uses_native_transport():
                params = (
                    parse_qsl(urlencode(query), keep_blank_values=True)
                    if query and method.upper() == "GET"
                    else []
                )
                body_bytes = (
                    json.dumps(query, separators=(",", ":")).encode()
                    if query and method.upper() != "GET"
                    else None
                )
                status, response_headers, response_body = await cast(
                    Any,
                    self._native_client,
                ).request_raw_async(
                    method,
                    path,
                    params,
                    body_bytes,
                    signed,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            else:
                if method.upper() == "GET":
                    if query:
                        query_string = urlencode(query)
                        url += f"?{query_string}"
                        full_path += f"?{query_string}"
                    response = await self.session.get(
                        url,
                        headers=self._headers(method, full_path, signed=signed),
                    )
                elif method.upper() == "POST":
                    body = json.dumps(query, separators=(",", ":")) if query else ""
                    response = await self.session.post(
                        url,
                        headers=self._headers(method, full_path, body, signed=signed),
                        content=body,
                    )
                elif method.upper() == "PUT":
                    body = json.dumps(query, separators=(",", ":")) if query else ""
                    response = await self.session.put(
                        url,
                        headers=self._headers(method, full_path, body, signed=signed),
                        content=body,
                    )
                elif method.upper() == "DELETE":
                    body = json.dumps(query, separators=(",", ":")) if query else ""
                    response = await self.session.request(
                        method="DELETE",
                        url=url,
                        headers=self._headers(method, full_path, body, signed=signed),
                        content=body,
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")

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

            timestamp = generate_timestamp(iso_format=True)

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
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data
