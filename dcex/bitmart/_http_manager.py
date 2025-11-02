"""Bitmart HTTP manager for handling API requests and authentication."""

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any

import msgspec
import requests

from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .endpoints.account import FundingAccount, FuturesAccount
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade


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
class HTTPManager:
    """
    HTTP manager for Bitmart API requests.

    This class handles authentication, request signing, and API communication
    for both spot and futures trading endpoints.
    """

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    memo: str | None = field(default=None)
    timeout: int = field(default=10)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
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

    def __post_init__(self) -> None:
        """Initialize logger and product table manager."""
        if self.logger is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = self.logger

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BITMART)

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

        if method.upper() == "GET" and query:
            params_str = "&".join(f"{k}={v}" for k, v in sorted(query.items()) if v)
            url = f"{url}?{params_str}"

        timestamp = generate_timestamp()

        if signed:
            if not (self.api_key and self.api_secret and self.memo):
                raise ValueError("Signed request requires API Key and Secret and Memo.")
            sign = sign_message(
                timestamp, self.memo, msgspec.json.encode(query).decode("utf-8"), self.api_secret
            )
            headers = get_header(self.api_key, sign, timestamp, self.memo)
        else:
            headers = get_header_no_sign()

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    json=query if query else {},
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            try:
                data = response.json()
            except Exception:
                data = {}

            if data.get("code", 0) != 1000:
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
            else:
                return data

        except requests.exceptions.RequestException as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=response.status_code if response else "Unknown",
                time=str(timestamp),
                resp_headers=dict(response.headers) if response else None,
            ) from e
