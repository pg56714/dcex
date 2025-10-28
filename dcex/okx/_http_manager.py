import base64
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


def _sign(message: str, secretKey: str) -> str:
    """
    Generate HMAC-SHA256 signature for OKX API authentication.

    Args:
        message: The message to sign (pre-hash string)
        secretKey: The API secret key

    Returns:
        Base64 encoded HMAC-SHA256 signature
    """
    mac = hmac.new(
        bytes(secretKey, encoding="utf8"),
        bytes(message, encoding="utf-8"),
        digestmod="sha256",
    )
    d = mac.digest()
    return base64.b64encode(d).decode()


def pre_hash(timestamp: str | int, method: str, path: str, body: str) -> str:
    """
    Create pre-hash string for OKX API signature generation.

    Args:
        timestamp: Request timestamp
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        body: Request body (empty string for GET requests)

    Returns:
        Concatenated string for signature generation
    """
    return str(timestamp) + str.upper(method) + path + body


def get_header(
    api_key: str, sign: str, timestamp: str | int, passphrase: str, flag: str
) -> dict[str, str]:
    """
    Generate HTTP headers for signed OKX API requests.

    Args:
        api_key: OKX API key
        sign: Generated signature
        timestamp: Request timestamp
        passphrase: OKX API passphrase
        flag: Simulated trading flag ("0" for live, "1" for simulated)

    Returns:
        Dictionary containing HTTP headers for authentication
    """
    header = {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": str(timestamp),
        "OK-ACCESS-PASSPHRASE": passphrase,
        "x-simulated-trading": flag,
    }
    return header


def parse_params_to_str(query: dict[str, Any]) -> str:
    """
    Convert query parameters dictionary to URL query string.

    Args:
        query: Dictionary of query parameters

    Returns:
        URL query string (e.g., "?param1=value1&param2=value2")
    """
    url = "?"
    for key, value in query.items():
        if value != "":
            url = url + str(key) + "=" + str(value) + "&"
    url = url[0:-1]
    return url


def get_header_no_sign(flag: str) -> dict[str, str]:
    """
    Generate HTTP headers for unsigned OKX API requests.

    Args:
        flag: Simulated trading flag ("0" for live, "1" for simulated)

    Returns:
        Dictionary containing basic HTTP headers
    """
    header = {
        "Content-Type": "application/json",
        "x-simulated-trading": flag,
    }
    return header


@dataclass
class HTTPManager:
    """
    HTTP manager for OKX API requests with authentication and error handling.

    This class handles all HTTP communication with the OKX API, including
    signature generation, request formatting, and error handling.

    Attributes:
        api_key: OKX API key for authentication
        api_secret: OKX API secret for signature generation
        passphrase: OKX API passphrase
        flag: Simulated trading flag ("0" for live, "1" for simulated)
        base_api: Base URL for OKX API
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retry attempts in seconds
        logger: Logger instance for debugging
        session: HTTP session for connection pooling
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
    """

    api_key: str | None = field(default=None)
    api_secret: str | None = field(default=None)
    passphrase: str | None = field(default=None)
    flag: str = field(default="0")
    base_api: str = field(default="https://www.okx.com")
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logger and optionally preloads the product table.
        """
        if self.logger is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = self.logger

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.OKX)

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | list[dict[str, Any]] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to OKX API with optional authentication.

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path
            query: Query parameters for GET requests or body for POST requests
            signed: Whether to include authentication headers

        Returns:
            JSON response data from the API

        Raises:
            ValueError: If signed request lacks required credentials
            FailedRequestError: If API returns error or HTTP request fails
        """
        if query is None:
            query = {}

        if method.upper() == "GET":
            if isinstance(query, dict):
                path += parse_params_to_str(query)
            else:
                # For GET requests with list query, convert to empty dict
                path += parse_params_to_str({})

        timestamp = generate_timestamp(iso_format=True)
        body = query if method.upper() == "POST" else ""
        body_str = (
            msgspec.json.encode(body).decode("utf-8") if isinstance(body, (dict, list)) else body
        )

        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key and Secret and Passphrase.")
            sign = _sign(pre_hash(timestamp, method.upper(), path, body_str), self.api_secret)
            headers = get_header(self.api_key, sign, timestamp, self.passphrase, self.flag)
        else:
            headers = get_header_no_sign(self.flag)

        url = self.base_api + path

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, data=body_str, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.RequestException as e:
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
