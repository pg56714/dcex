import base64
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import urlencode

import msgspec
import requests

from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp


def _sign(plain: bytes, key: bytes) -> str:
    """KuCoin signature generation using HMAC-SHA256."""
    hm = hmac.new(key, plain, hashlib.sha256)
    return base64.b64encode(hm.digest()).decode()


@dataclass
class HTTPManager(BaseHTTPManager):
    EXCHANGE = Common.KUCOIN

    base_url: str = field(default="https://api.kucoin.com")
    futures_base_url: str = field(default="https://api-futures.kucoin.com")
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    passphrase: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _encrypted_passphrase: str | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self.logger or logging.getLogger(__name__)

        if self.passphrase and self.api_secret:
            self._encrypted_passphrase = _sign(
                self.passphrase.encode("utf-8"), self.api_secret.encode("utf-8")
            )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.KUCOIN)

    def _generate_headers(self, timestamp: str, signature: str) -> dict[str, str]:
        """Generate headers for KuCoin API requests."""
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key and signature and self._encrypted_passphrase:
            headers.update(
                {
                    "KC-API-KEY": self.api_key,
                    "KC-API-SIGN": signature,
                    "KC-API-TIMESTAMP": timestamp,
                    "KC-API-PASSPHRASE": self._encrypted_passphrase,
                    "KC-API-KEY-VERSION": "2",
                }
            )

        return headers

    def _create_signature_payload(self, timestamp: str, method: str, path: str, body: str) -> str:
        """Create the payload for signature generation according to KuCoin API v2."""
        return f"{timestamp}{method.upper()}{path}{body}"

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to KuCoin API."""
        timestamp = str(int(time.time() * 1000))
        body = ""
        request_path = path
        signature_path = path

        if method.upper() == "GET":
            if query:
                request_path = f"{path}?{urlencode(query)}"
                signature_path = request_path
        elif method.upper() in {"POST", "PUT"}:
            body = msgspec.json.encode(query).decode("utf-8") if query else ""
        elif method.upper() == "DELETE":
            if query:
                query_string = urlencode(query)
                request_path = f"{path}?{query_string}"
                signature_path = request_path

        signature = ""
        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key, Secret, and Passphrase.")

            payload = self._create_signature_payload(timestamp, method, signature_path, body)
            signature = _sign(payload.encode("utf-8"), self.api_secret.encode("utf-8"))

        response = None
        url = f"{base_url or self.base_url}{request_path}"
        try:
            headers = self._generate_headers(timestamp, signature)
            method_upper = method.upper()

            if method_upper == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method_upper == "POST":
                response = self.session.post(url, headers=headers, data=body, timeout=self.timeout)
            elif method_upper == "PUT":
                response = self.session.put(url, headers=headers, data=body, timeout=self.timeout)
            elif method_upper == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

        except requests.RequestException as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {e}",
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
                    request=f"{method} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                ) from exc

            timestamp_str = str(generate_timestamp(iso_format=True))

            if isinstance(data, dict) and data.get("code") != "200000":
                code = data.get("code", "Unknown")
                error_message = data.get("msg", "Unknown error")
                raise FailedRequestError(
                    request=f"{method} {url} | Body: {query}",
                    message=f"KUCOIN API Error: [{code}] {error_message}",
                    status_code=response.status_code,
                    time=timestamp_str,
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=timestamp_str,
                    resp_headers=dict(response.headers),
                )

            return data

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
