"""BingX sync HTTP manager for API requests."""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import requests

from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError


def get_header(api_key: str) -> dict[str, str]:
    return {
        "X-BX-APIKEY": api_key,
    }


def get_header_no_sign() -> dict[str, str]:
    return {"Content-Type": "application/json"}


def get_sign(api_secret: str, payload: str) -> str:
    signature = hmac.new(
        api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()
    return signature


def _format_param_value(value: object) -> str:
    if isinstance(value, dict | list):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _prepare_query(params_map: dict[str, Any]) -> dict[str, str]:
    return {
        key: _format_param_value(value)
        for key, value in sorted(params_map.items())
        if value is not None
    }


def _build_param_string(params_map: dict[str, str], *, encode: bool) -> str:
    if encode:
        return urlencode(params_map)
    return "&".join(f"{key}={value}" for key, value in params_map.items())


def signed_param_strings(params_map: dict[str, Any]) -> tuple[str, str]:
    params = _prepare_query(params_map)
    params["timestamp"] = str(int(time.time() * 1000))
    return (
        _build_param_string(params, encode=False),
        _build_param_string(params, encode=True),
    )


def parse_param(params_map: dict[str, Any]) -> str:
    params = _prepare_query(params_map)
    params["timestamp"] = str(int(time.time() * 1000))
    return _build_param_string(params, encode=False)


@dataclass
class HTTPManager:
    """HTTP manager for BingX API requests with authentication and error handling."""

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    max_retries: int = field(default=3)
    retry_delay: int = field(default=3)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    base_url: str = field(default="https://open-api.bingx.com")

    def __post_init__(self) -> None:
        """Initialize the HTTP manager."""
        self._logger = self.logger or logging.getLogger(__name__)
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.BINGX)

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """Make an HTTP request to BingX API."""
        if signed:
            if not (self.api_key and self.api_secret):
                raise ValueError("Signed request requires API Key and Secret.")

            sign_payload, urlpa = signed_param_strings(query or {})
            url = (
                f"{self.base_url}{path}?{urlpa}&signature={get_sign(self.api_secret, sign_payload)}"
            )
            headers = get_header(self.api_key)
        else:
            headers = get_header_no_sign()
            url = self.base_url + path
            if query:
                sorted_query = urlencode(_prepare_query(query))
                url += "?" + sorted_query if sorted_query else ""

        response = None
        try:
            method_upper = method.upper()
            if method_upper == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method_upper == "POST":
                response = self.session.post(url, headers=headers, timeout=self.timeout)
            elif method_upper == "PUT":
                response = self.session.put(url, headers=headers, timeout=self.timeout)
            elif method_upper == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except requests.RequestException as e:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {e}",
                status_code=response.status_code if response else "Unknown",
                time=str(int(time.time() * 1000)),
                resp_headers=dict(response.headers) if response else None,
            ) from e
        else:
            try:
                data = {"code": 0} if not response.content else response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(int(time.time() * 1000)),
                    resp_headers=dict(response.headers),
                ) from exc

            if data.get("code", 0) != 0:
                code = data.get("code", "Unknown")
                error_message = data.get("msg", "Unknown error")
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"BingX API Error: [{code}] {error_message}",
                    status_code=response.status_code,
                    time=str(int(time.time() * 1000)),
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(int(time.time() * 1000)),
                    resp_headers=dict(response.headers),
                )

            return data

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
