"""OKX HTTP manager for handling API requests."""

import base64
import hmac
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


def _sign(message: str, secretKey: str) -> str:
    """
    Generate HMAC-SHA256 signature.

    Args:
        message: Message to sign
        secretKey: Secret key for signing

    Returns:
        Base64 encoded signature
    """
    mac = hmac.new(
        bytes(secretKey, encoding="utf8"),
        bytes(message, encoding="utf-8"),
        digestmod="sha256",
    )
    d = mac.digest()
    return base64.b64encode(d).decode()


def pre_hash(timestamp: str, method: str, path: str, body: str) -> str:
    """
    Create pre-hash string for signature.

    Args:
        timestamp: Request timestamp
        method: HTTP method
        path: Request path
        body: Request body

    Returns:
        Pre-hash string
    """
    return str(timestamp) + str.upper(method) + path + body


def get_header(
    api_key: str, sign: str, timestamp: str, passphrase: str, flag: str
) -> dict[str, str]:
    """
    Generate signed request headers.

    Args:
        api_key: API key
        sign: Request signature
        timestamp: Request timestamp
        passphrase: API passphrase
        flag: Simulated trading flag

    Returns:
        Dict containing request headers
    """
    return {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": str(timestamp),
        "OK-ACCESS-PASSPHRASE": passphrase,
        "x-simulated-trading": flag,
    }


def get_header_no_sign(flag: str) -> dict[str, str]:
    """
    Generate unsigned request headers.

    Args:
        flag: Simulated trading flag

    Returns:
        Dict containing request headers
    """
    return {
        "Content-Type": "application/json",
        "x-simulated-trading": flag,
    }


def parse_params_to_str(query: dict[str, Any]) -> str:
    """
    Parse query parameters to URL string.

    Args:
        query: Query parameters dictionary

    Returns:
        URL query string, or empty string when *query* is empty.
    """
    parts = [f"{key}={value}" for key, value in query.items() if value != ""]
    if not parts:
        return ""
    return "?" + "&".join(parts)


def _okx_error_details(data: dict[str, Any]) -> tuple[str, str]:
    api_code = str(data.get("code", "Unknown"))
    error_message = str(data.get("msg") or "Unknown error")
    rows = data.get("data")
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        api_code = str(rows[0].get("sCode") or api_code)
        error_message = str(rows[0].get("sMsg") or error_message)
    return api_code, error_message


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for OKX API requests."""

    EXCHANGE = Common.OKX

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    passphrase: str | None = field(default=None, repr=False)
    flag: str = field(default="0")
    base_api: str = field(default="https://openapi.okx.com")
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: Any = field(default=None, init=False, repr=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager.

        Returns:
            Self instance
        """
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.OKX)
        native_client_type = getattr(_native, "OkxHttpClient", None)
        if self.use_native and native_client_type is not None and self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                passphrase=self.passphrase,
                flag=self.flag,
                timeout=self.timeout,
                base_url=self.base_api,
            )
        if self.preload_product_table and self._native_client is not None:
            self._native_client.set_product_table(self.ptm._native_table)
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
        """Call a Rust-backed OKX private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for private methods.")
        try:
            status, headers, body = await self._native_client.private_request_async(
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"OKX {method_name} | Params: {params}",
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
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to OKX API.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path
            query: Query parameters or request body
            signed: Whether to sign the request

        Returns:
            Dict containing API response

        Raises:
            FailedRequestError: If request fails
        """
        if self._native_client is None:
            await self.async_init()

        if query is None:
            query = {}

        method_upper = method.upper()
        request_path = path
        if method_upper == "GET" and query and isinstance(query, dict):
            request_path += parse_params_to_str(query)

        timestamp = generate_timestamp(iso_format=True)
        body = query if method_upper == "POST" else ""
        body_str = (
            json.dumps(body, separators=(",", ":")) if isinstance(body, (dict, list)) else body
        )

        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key and Secret and Passphrase.")
            if not self._uses_native_transport():
                sign = _sign(
                    pre_hash(str(timestamp), method_upper, request_path, body_str),
                    self.api_secret,
                )
                headers = get_header(
                    self.api_key,
                    sign,
                    str(timestamp),
                    self.passphrase,
                    self.flag,
                )
            else:
                headers = get_header_no_sign(self.flag)
        else:
            headers = get_header_no_sign(self.flag)

        url = self.base_api + request_path
        self._log_request(method, url)

        try:
            if self._uses_native_transport():
                params = (
                    [(key, str(value)) for key, value in query.items()]
                    if method_upper == "GET" and isinstance(query, dict)
                    else []
                )
                status, response_headers, response_body = await cast(
                    Any,
                    self._native_client,
                ).request_raw_async(
                    method,
                    path,
                    params,
                    body_str.encode() if method_upper == "POST" else None,
                    signed,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            elif method_upper == "GET":
                response = await self.session.get(url, headers=headers)
            elif method_upper == "POST":
                # Send exactly the same JSON string used for signing to avoid signature mismatch
                response = await self.session.post(url, headers=headers, content=body_str)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except RuntimeError as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {query}",
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
                    request=f"{method_upper} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                ) from exc
            if not isinstance(data, dict):
                raise FailedRequestError(
                    request=f"{method_upper} {url} | Body: {query}",
                    message=f"Unexpected response type: {type(data).__name__}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            if data.get("code", "0") != "0":
                api_code, error_message = _okx_error_details(data)
                self._log_failed_request(f"OKX API Error: [{api_code}] {error_message}", api_code)
                raise FailedRequestError(
                    request=f"{method_upper} {url} | Body: {query}",
                    message=f"OKX API Error: [{api_code}] {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method_upper} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data
