import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Self

import httpx
import msgspec

from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager
from .endpoints.account import FundingAccount, FuturesAccount
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade


def sign_message(timestamp: int, memo: str, body: str, secret_key: str) -> str:
    message = f"{timestamp}#{memo}#{body}"
    return hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def get_header(api_key: str, sign: str, timestamp: int, memo: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-BM-KEY": api_key,
        "X-BM-SIGN": sign,
        "X-BM-TIMESTAMP": str(timestamp),
        "X-BM-MEMO": memo,
    }


def get_header_no_sign() -> dict[str, str]:
    return {"Content-Type": "application/json"}


@dataclass
class HTTPManager:
    """HTTP manager for BitMart API requests with authentication and error handling."""

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    memo: str | None = field(default=None)
    timeout: int = field(default=10)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(init=False, default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

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

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager.

        Returns:
            HTTPManager: Initialized HTTP manager instance
        """
        self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self.logger or logging.getLogger(__name__)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BITMART)
        return self

    def _get_base_url(
        self,
        path: FundingAccount
        | FuturesAccount
        | SpotMarket
        | FuturesMarket
        | SpotTrade
        | FuturesTrade,
    ) -> str:
        """
        Get base URL for API endpoint.

        Args:
            path: API endpoint path

        Returns:
            str: Base URL for the endpoint

        Raises:
            ValueError: When unknown API path is provided
        """
        for base_url, enums in self.api_map.items():
            if type(path) in enums:
                return base_url
        raise ValueError(f"Unknown API path: {path} (type={type(path)})")

    async def _request(
        self,
        method: Literal["GET", "POST"],
        path: FundingAccount
        | FuturesAccount
        | SpotMarket
        | FuturesMarket
        | SpotTrade
        | FuturesTrade,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to BitMart API.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path
            query: Query parameters
            signed: Whether to sign the request

        Returns:
            dict: API response data

        Raises:
            ValueError: When API credentials are missing for signed requests
            FailedRequestError: When API request fails
        """
        if self.session is None or self.session.is_closed:
            await self.async_init()

        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session")

        if query is None:
            query = {}

        base_url = self._get_base_url(path)
        url = base_url + path.value

        if method.upper() == "GET" and query:
            params_str = "&".join(f"{k}={v}" for k, v in sorted(query.items()) if v)
            url = f"{url}?{params_str}"

        timestamp = generate_timestamp()

        if signed:
            if not (self.api_key and self.api_secret and self.memo):
                raise ValueError("Signed request requires API Key and Secret and Memo.")

            body = (
                ""
                if method.upper() == "GET"
                else msgspec.json.encode(query if query else {}).decode("utf-8")
            )
            sign = sign_message(int(timestamp), self.memo, body, self.api_secret)
            headers = get_header(self.api_key, sign, int(timestamp), self.memo)
        else:
            headers = get_header_no_sign()

        response = None
        try:
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                # Use data instead of json to ensure exact body matches signature
                response = await self.session.post(
                    url,
                    content=body,
                    headers=headers,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except httpx.HTTPError as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=response.status_code if response else "Unknown",
                time=str(timestamp),
                resp_headers=dict(response.headers) if response else None,
            ) from e
        else:
            try:
                data = response.json()
            except Exception:
                data = {}

            if data.get("code", 0) != 1000:
                print(data)
                code = data.get("code", "Unknown")
                error_msg = data.get("msg") or data.get("message") or "Unknown error"
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

            return data
