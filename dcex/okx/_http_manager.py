import base64
import hmac
import logging
from dataclasses import dataclass, field
from typing import Any

import msgspec
import requests

from ..base.http_manager import BaseHTTPManager
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
        URL query string (e.g., "?param1=value1&param2=value2"), or empty
        string when *query* is empty.
    """
    parts = [f"{key}={value}" for key, value in query.items() if value != ""]
    if not parts:
        return ""
    return "?" + "&".join(parts)


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
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
        session: HTTP session for connection pooling
        ptm: Product table manager instance
        preload_product_table: Whether to preload product table
    """

    EXCHANGE = Common.OKX

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    passphrase: str | None = field(default=None, repr=False)
    flag: str = field(default="0")
    base_api: str = field(default="https://openapi.okx.com")
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    def __post_init__(self) -> None:
        """
        Initialize the HTTP manager after dataclass creation.

        Sets up logger and optionally preloads the product table.
        """
        self._logger = self._setup_logger(self.logger)

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
        self._log_request(method, url)

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    data=body_str,
                    headers=headers,
                    timeout=self.timeout,
                )
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
            if not isinstance(data, dict):
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Unexpected response type: {type(data).__name__}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            if data.get("code", "0") != "0":
                api_code, error_message = _okx_error_details(data)
                self._log_failed_request(f"OKX API Error: [{api_code}] {error_message}", api_code)
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"OKX API Error: [{api_code}] {error_message}",
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
