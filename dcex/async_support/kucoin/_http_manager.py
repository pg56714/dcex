import base64
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import urlencode

import httpx
import msgspec

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


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
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _encrypted_passphrase: str | None = field(default=None, init=False, repr=False)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self.logger or logging.getLogger(__name__)

        # Encrypt passphrase if credentials are provided
        if self.passphrase and self.api_secret:
            self._encrypted_passphrase = _sign(
                self.passphrase.encode("utf-8"), self.api_secret.encode("utf-8")
            )
        native_client_type = getattr(_native, "KucoinHttpClient", None)
        if self.use_native and native_client_type is not None and self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                passphrase=self.passphrase,
                timeout=self.timeout,
                spot_base_url=self.base_url,
                futures_base_url=self.futures_base_url,
            )

        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.KUCOIN)
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        if (
            self.preload_product_table
            and self._native_client is not None
            and hasattr(self._native_client, "set_product_table")
        ):
            self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self, request_base_url: str) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is httpx.AsyncClient
            and request_base_url in {self.base_url, self.futures_base_url}
        )

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed KuCoin private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("KuCoin native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_async"):
            raise RuntimeError("KuCoin native client private_request_async is unavailable.")
        try:
            status, headers, body = await self._native_client.private_request_async(
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"KUCOIN {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            if key == "from_":
                key = "from"
            elif key == "type_":
                key = "type"
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = msgspec.json.encode(value).decode("utf-8")
            params.append((key, str(value)))
        return params

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
        # For KuCoin API v2, the signature payload is: timestamp + method + path + body
        return f"{timestamp}{method.upper()}{path}{body}"

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to KuCoin API."""
        if self.session is None or self.session.is_closed:
            await self.async_init()

        # 再次檢查確保 session 不為 None
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session")

        # Prepare request data
        timestamp = str(int(time.time() * 1000))
        method_upper = method.upper()
        body = ""
        request_path = path
        signature_path = path

        # Handle different HTTP methods
        if method_upper == "GET":
            if query:
                request_path = f"{path}?{urlencode(query)}"
                signature_path = (
                    f"{path}?{urlencode(query)}"  # GET: include query params in signature
                )
        elif method_upper in ["POST", "PUT"]:
            body = msgspec.json.encode(query).decode("utf-8") if query else ""
            # POST/PUT/DELETE: don't include query params in signature path
            signature_path = path
        elif method_upper == "DELETE":
            if query:
                query_string = urlencode(query)
                request_path = f"{path}?{query_string}"
                signature_path = f"{path}?{query_string}"
            else:
                request_path = path
                signature_path = path

        # Generate signature if needed
        request_base_url = base_url or self.base_url
        uses_native = self._uses_native_transport(request_base_url)
        signature = ""
        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key, Secret, and Passphrase.")

            # Create signature payload
            if not uses_native:
                payload = self._create_signature_payload(timestamp, method, signature_path, body)
                if self.api_secret is None:
                    raise ValueError("API secret is required for signing")
                signature = _sign(payload.encode("utf-8"), self.api_secret.encode("utf-8"))

        response = None
        url = f"{request_base_url}{request_path}"
        try:
            if uses_native:
                market = "futures" if request_base_url == self.futures_base_url else "spot"
                status, response_headers, response_body = await cast(
                    Any,
                    self._native_client,
                ).request_raw_async(
                    method,
                    market,
                    path,
                    [(key, str(value)) for key, value in (query or {}).items()],
                    body.encode() if body else None,
                    signed,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            elif method_upper == "GET":
                headers = self._generate_headers(timestamp, signature)
                response = await self.session.get(url, headers=headers)
            elif method_upper == "POST":
                headers = self._generate_headers(timestamp, signature)
                response = await self.session.post(url, headers=headers, content=body)
            elif method_upper == "PUT":
                headers = self._generate_headers(timestamp, signature)
                response = await self.session.put(url, headers=headers, content=body)
            elif method_upper == "DELETE":
                headers = self._generate_headers(timestamp, signature)
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

        except (httpx.RequestError, RuntimeError) as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
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

            # Check for KuCoin API errors
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

            # Check HTTP status code
            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=timestamp_str,
                    resp_headers=dict(response.headers),
                )

            return data

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.aclose()
