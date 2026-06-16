import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, cast
from urllib.parse import urlencode

import requests

from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .endpoints.account import FuturesAccount, SpotAccount, WalletAsset
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade

try:
    _native = import_module("dcex._native")
except ImportError:
    _native = None


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
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    api_map = {
        "https://fapi.binance.com": {
            FuturesTrade,
            FuturesMarket,
            FuturesAccount,
        },
        "https://api.binance.com": {
            SpotMarket,
            SpotTrade,
            SpotAccount,
            WalletAsset,
        },
    }

    def __post_init__(self) -> None:
        """Initialize the HTTP manager after dataclass creation."""
        self._logger = self._setup_logger(self.logger)

        if self.use_native and _native is not None:
            self._native_client = _native.BinanceHttpClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
            )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BINANCE)
            if self._native_client is not None:
                self._native_client.set_product_table(self.ptm._native_table)

    def _get_base_url(
        self,
        path: (
            SpotAccount
            | FuturesAccount
            | WalletAsset
            | SpotMarket
            | FuturesMarket
            | SpotTrade
            | FuturesTrade
        ),
    ) -> str:
        for base_url, enums in self.api_map.items():
            if type(path) in enums:
                return base_url
        raise ValueError(f"Unknown API path: {path} (type={type(path)})")

    def _sign(self, params: dict[str, Any]) -> str:
        """
        Sign the request parameters using HMAC SHA256.

        Args:
            params: Dictionary of request parameters to sign.

        Returns:
            str: The HMAC signature as a hexadecimal string.

        Raises:
            ValueError: If API secret is not provided.
        """
        if self.api_secret is None:
            raise ValueError("API secret is required for signing requests")
        query_string = urlencode(params)
        return hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    def _headers(self) -> dict[str, str]:
        """
        Get HTTP headers for API requests.

        Returns:
            dict[str, str]: Headers dictionary with API key if available.
        """
        return {"X-MBX-APIKEY": self.api_key} if self.api_key else {}

    @staticmethod
    def _native_market(
        path: (
            SpotAccount
            | FuturesAccount
            | WalletAsset
            | SpotMarket
            | FuturesMarket
            | SpotTrade
            | FuturesTrade
        ),
    ) -> str:
        if type(path) in {FuturesTrade, FuturesMarket, FuturesAccount}:
            return "futures"
        return "spot"

    def _uses_native_transport(self) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is requests.Session
        )

    def _request(
        self,
        method: str,
        path: (
            SpotAccount
            | FuturesAccount
            | WalletAsset
            | SpotMarket
            | FuturesMarket
            | SpotTrade
            | FuturesTrade
        ),
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

        base_url = self._get_base_url(path)
        url = f"{base_url}{path}"
        self._log_request(method, url)
        uses_native = self._uses_native_transport()
        native_client = self._native_client
        response = None
        try:
            if uses_native:
                status_code, response_headers, body = cast(Any, native_client).request_raw(
                    method,
                    self._native_market(path),
                    str(path),
                    [(str(key), str(value)) for key, value in query.items()],
                    signed,
                )
                response_headers = dict(response_headers)
                response_text = bytes(body).decode(errors="replace")
                self.last_response_headers = response_headers
            else:
                if signed:
                    query["timestamp"] = int(time.time() * 1000)
                    query["recvWindow"] = 5000
                    query["signature"] = self._sign(query)

                if method.upper() == "GET":
                    url += f"?{urlencode(query)}" if query else ""
                    response = self.session.get(
                        url,
                        headers=self._headers(),
                        timeout=self.timeout,
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url,
                        headers=self._headers(),
                        timeout=self.timeout,
                        data=query,
                    )
                elif method.upper() == "PUT":
                    response = self.session.put(
                        url,
                        headers=self._headers(),
                        timeout=self.timeout,
                        data=query,
                    )
                elif method.upper() == "DELETE":
                    url += f"?{urlencode(query)}" if query else ""
                    response = self.session.delete(
                        url,
                        headers=self._headers(),
                        timeout=self.timeout,
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response_headers = self._store_response_headers(response)
                status_code = response.status_code
                response_text = response.text
        except (requests.exceptions.RequestException, RuntimeError) as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(exc)}",
                status_code=status_code,
                time=query.get("timestamp", "Unknown"),
                resp_headers=resp_headers,
            ) from exc

        try:
            if uses_native:
                data = json.loads(body)
            else:
                data = cast(Any, response).json()
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
        """Close the HTTP session."""
        self.session.close()
