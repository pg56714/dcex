"""OKX HTTP manager for handling API requests."""

import base64
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any, Self

import httpx
import msgspec

from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


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
        URL query string
    """
    url = "?"
    for key, value in query.items():
        if value != "":
            url += f"{key}={value}&"
    return url.rstrip("&")


@dataclass
class HTTPManager:
    """HTTP manager for OKX API requests."""

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    passphrase: str | None = field(default=None)
    flag: str = field(default="0")
    base_api: str = field(default="https://www.okx.com")
    timeout: int = field(default=10)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager.

        Returns:
            Self instance
        """
        self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self.logger or logging.getLogger(__name__)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.OKX)
        return self

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
        if self.session is None or self.session.is_closed:
            await self.async_init()

        if query is None:
            query = {}

        if method.upper() == "GET" and query and isinstance(query, dict):
            path += parse_params_to_str(query)

        timestamp = generate_timestamp(iso_format=True)
        body = query if method.upper() == "POST" else ""
        body_str = (
            msgspec.json.encode(body).decode("utf-8") if isinstance(body, (dict, list)) else body
        )

        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key and Secret and Passphrase.")
            sign = _sign(pre_hash(str(timestamp), method.upper(), path, body_str), self.api_secret)
            headers = get_header(self.api_key, sign, str(timestamp), self.passphrase, self.flag)
        else:
            headers = get_header_no_sign(self.flag)

        url = self.base_api + path

        try:
            if self.session is None:
                raise ValueError("Session is not initialized")
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                # Send exactly the same JSON string used for signing to avoid signature mismatch
                response = await self.session.post(url, headers=headers, content=body_str)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except httpx.HTTPError as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code="Unknown",
                time=str(timestamp),
                resp_headers=None,
            ) from e
        else:
            try:
                data = response.json()
            except Exception:
                data = {}

            if data.get("code", "0") != "0":
                status_code = data.get("data", [{}])[0].get("sCode", "Unknown")
                error_message = data.get("data", [{}])[0].get("sMsg", "Unknown error")
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"OKX API Error: [{status_code}] {error_message}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data
