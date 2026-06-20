import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Self, cast
from urllib.parse import urlencode

from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager
from .endpoints.account import FuturesAccount, SpotAccount, WalletAsset
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade

try:
    _native = import_module("dcex._native")
except ImportError:
    _native = None


@dataclass
class HTTPManager(BaseHTTPManager):
    EXCHANGE = Common.BINANCE

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: Any = field(default=None, init=False, repr=False)
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

    async def async_init(self) -> Self:
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BINANCE)
        if self.use_native and _native is not None and self._native_client is None:
            self._native_client = _native.BinanceHttpClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
            )
        if self.preload_product_table and self._native_client is not None:
            self._native_client.set_product_table(self.ptm._native_table)
        return self

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

    def _sign(self, params: dict) -> str:
        if self.api_secret is None:
            raise ValueError("API secret is required for signing")
        query_string = urlencode(params)
        return hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    def _headers(self) -> dict[str, str]:
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
        if not self.use_native or self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _request(
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
    ) -> dict:
        if self._native_client is None:
            await self.async_init()

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
                status_code, response_headers, body = await cast(
                    Any,
                    native_client,
                ).request_raw_async(
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
                    response = await self.session.get(url, headers=self._headers())
                elif method.upper() == "POST":
                    response = await self.session.post(
                        url,
                        headers=self._headers(),
                        data=query,
                    )
                elif method.upper() == "PUT":
                    response = await self.session.put(
                        url,
                        headers=self._headers(),
                        data=query,
                    )
                elif method.upper() == "DELETE":
                    url += f"?{urlencode(query)}" if query else ""
                    response = await self.session.delete(url, headers=self._headers())
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response_headers = self._store_response_headers(response)
                status_code = response.status_code
                response_text = response.text
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Params: {query}",
                message=f"Request failed: {str(exc)}",
                status_code=status_code,
                time=str(query.get("timestamp", "Unknown")),
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
