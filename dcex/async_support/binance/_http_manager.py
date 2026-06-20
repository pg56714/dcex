import json
import logging
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
    EXCHANGE = Common.BINANCE

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BINANCE)
        if self._native_client is None:
            self._native_client = _native.BinanceHttpClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
            )
        if self.preload_product_table and self._native_client is not None:
            self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _request(
        self,
        method: str,
        path: str,
        query: dict | None = None,
        signed: bool = True,
    ) -> dict:
        if self._native_client is None:
            await self.async_init()

        query = dict(query or {})
        if signed and not (self.api_key and self.api_secret):
            raise ValueError("Signed request requires API Key and Secret.")

        request_path = str(path)
        url = request_path
        self._log_request(method, url)
        self._uses_native_transport()
        native_client = cast(Any, self._native_client)
        try:
            status_code, response_headers, body = await native_client.request_raw_auto_async(
                method,
                request_path,
                [(str(key), str(value)) for key, value in query.items()],
                signed,
            )
            response_headers = dict(response_headers)
            response_text = bytes(body).decode(errors="replace")
            self.last_response_headers = response_headers
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
            data = json.loads(body)
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
