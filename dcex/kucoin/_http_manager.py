import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import urlencode

from .._native_http import NativeResponse, load_native, native_body_text, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()


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
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self.logger or logging.getLogger(__name__)

        native_client_type = getattr(_native, "KucoinHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        self._native_client = native_client_type(
            api_key=self.api_key,
            api_secret=self.api_secret,
            passphrase=self.passphrase,
            timeout=self.timeout,
            spot_base_url=self.base_url,
            futures_base_url=self.futures_base_url,
        )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.KUCOIN)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed KuCoin private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("KuCoin native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_json"):
            raise RuntimeError("KuCoin native client private_request_json is unavailable.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
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
        self._store_response_headers(response)
        return data

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
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to KuCoin API."""
        timestamp = str(generate_timestamp(iso_format=True))
        method_upper = method.upper()
        body = ""
        request_path = path

        if method_upper == "GET":
            if query:
                request_path = f"{path}?{urlencode(query)}"
        elif method_upper in {"POST", "PUT"}:
            body = json.dumps(query, separators=(",", ":")) if query else ""
        elif method_upper == "DELETE":
            if query:
                query_string = urlencode(query)
                request_path = f"{path}?{query_string}"
        else:
            raise ValueError(f"Unsupported method: {method}")

        request_base_url = base_url or self.base_url
        self._uses_native_transport()
        if signed:
            if not (self.api_key and self.api_secret and self.passphrase):
                raise ValueError("Signed request requires API Key, Secret, and Passphrase.")

        url = f"{request_base_url}{request_path}"
        try:
            market = "futures" if request_base_url == self.futures_base_url else "spot"
            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw_json(
                method,
                market,
                path,
                [(key, str(value)) for key, value in (query or {}).items()],
                body.encode() if body else None,
                signed,
            )
            response = NativeResponse(status, dict(response_headers))

        except RuntimeError as e:
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
            data = response_body
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
                    message=f"HTTP Error {response.status_code}: {native_body_text(data)}",
                    status_code=response.status_code,
                    time=timestamp_str,
                    resp_headers=dict(response.headers),
                )

            return data

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
