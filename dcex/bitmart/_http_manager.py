"""Bitmart HTTP manager for handling API requests and authentication."""

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any, cast

import msgspec
import requests

from .._native_http import NativeResponse, load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .endpoints.account import FundingAccount, FuturesAccount
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade

_native = load_native()


def sign_message(timestamp: int, memo: str, body: str, secret_key: str) -> str:
    """
    Generate HMAC signature for Bitmart API authentication.

    Args:
        timestamp: Request timestamp
        memo: API memo
        body: Request body
        secret_key: API secret key

    Returns:
        HMAC signature string
    """
    message = f"{timestamp}#{memo}#{body}"
    return hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def get_header(api_key: str, sign: str, timestamp: int, memo: str) -> dict[str, str]:
    """
    Generate HTTP headers for signed requests.

    Args:
        api_key: API key
        sign: HMAC signature
        timestamp: Request timestamp
        memo: API memo

    Returns:
        Dictionary containing HTTP headers
    """
    return {
        "Content-Type": "application/json",
        "X-BM-KEY": api_key,
        "X-BM-SIGN": sign,
        "X-BM-TIMESTAMP": str(timestamp),
        "X-BM-MEMO": memo,
    }


def get_header_no_sign() -> dict[str, str]:
    """
    Generate HTTP headers for unsigned requests.

    Returns:
        Dictionary containing basic HTTP headers
    """
    return {"Content-Type": "application/json"}


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
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    api_map = {
        "https://api-cloud.bitmart.com": {
            SpotTrade,
            SpotMarket,
            FundingAccount,
        },  # v1 API
        "https://api-cloud-v2.bitmart.com": {
            FuturesTrade,
            FuturesMarket,
            FuturesAccount,
        },  # v2 API
    }

    def __post_init__(self) -> None:
        """Initialize logger and product table manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "BitmartHttpClient", None)
        if self.use_native and native_client_type is not None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                memo=self.memo,
                timeout=self.timeout,
            )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BITMART)

    @staticmethod
    def _native_market(path: str) -> str:
        if type(path) in {FuturesTrade, FuturesMarket, FuturesAccount}:
            return "futures"
        return "spot"

    def _uses_native_transport(self) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is requests.Session
        )

    def _get_base_url(self, path: str) -> str:
        """
        Get the base URL for the given API path.

        Args:
            path: API endpoint path

        Returns:
            Base URL string

        Raises:
            ValueError: If the path type is not recognized
        """
        for base_url, enums in self.api_map.items():
            if type(path) in enums:
                return base_url
        raise ValueError(f"Unknown API path: {path} (type={type(path)})")

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

        base_url = self._get_base_url(path)
        url = base_url + str(path)

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
            msgspec.json.encode(query if query else {}).decode("utf-8")
            if method_upper == "POST"
            else ""
        )

        if signed and not (self.api_key and self.api_secret and self.memo):
            raise ValueError("Signed request requires API Key and Secret and Memo.")

        if signed:
            memo = cast(str, self.memo)
            sign = sign_message(timestamp, memo, body, cast(str, self.api_secret))
            headers = get_header(cast(str, self.api_key), sign, timestamp, memo)
        else:
            headers = get_header_no_sign()

        self._log_request(method, url)

        response = None
        try:
            if self._uses_native_transport():
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
                ).request_raw(
                    method,
                    self._native_market(path),
                    str(path),
                    params,
                    body.encode() if method_upper == "POST" else None,
                    signed,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            else:
                if method_upper == "GET":
                    response = self.session.get(url, headers=headers, timeout=self.timeout)
                elif method_upper == "POST":
                    response = self.session.post(
                        url,
                        data=body,
                        headers=headers,
                        timeout=self.timeout,
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                ) from exc

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
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )
            else:
                return data

        except (requests.exceptions.RequestException, RuntimeError) as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=resp_headers,
            ) from e

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
