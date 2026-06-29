"""BingX HTTP manager for API requests."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


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


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for BingX API requests with authentication and error handling."""

    EXCHANGE = Common.BINGX

    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    base_url: str = field(default="https://open-api.bingx.com")
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager.

        Returns:
            HTTPManager: Initialized HTTP manager instance
        """
        self._logger = self.logger or logging.getLogger(__name__)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.BINGX)
        native_client_type = getattr(_native, "BingxHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                api_key=self.api_key,
                api_secret=self.api_secret,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if (
            self.preload_product_table
            and self._native_client is not None
            and hasattr(self._native_client, "set_product_table")
        ):
            self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BingX private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BingX native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_async"):
            raise RuntimeError("BingX native client private_request_async is unavailable.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BingX {method_name} | Params: {params}",
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
            if value is None:
                continue
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, dict | list | tuple):
                value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: str,
        path: str,
        query: dict | None = None,
        signed: bool = True,
        request_headers: dict[str, str] | None = None,
    ) -> dict:
        """
        Make an HTTP request to BingX API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            query: Query parameters
            signed: Whether to sign the request

        Returns:
            dict: API response data

        Raises:
            ValueError: When API credentials are missing for signed requests
            FailedRequestError: When API request fails
        """

        if self._native_client is None:
            await self.async_init()

        if signed and not (self.api_key and self.api_secret):
            raise ValueError("Signed request requires API Key and Secret.")

        self._uses_native_transport()
        url = self.base_url + path
        try:
            json_body = None
            if not signed and method.upper() in {"POST", "PUT"}:
                json_body = json.dumps(
                    query or {},
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode()
            status, response_headers, body = await cast(Any, self._native_client).request_raw_async(
                method,
                path,
                list(_prepare_query(query or {}).items()),
                signed,
                None if signed else request_headers,
                json_body,
            )
            response = NativeResponse(status, dict(response_headers), bytes(body))

        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(exc)}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc
        else:
            self._store_response_headers(response)
            try:
                data = {"code": 0} if not response.content else response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                ) from exc

            if data.get("code", 0) != 0:
                code = data.get("code", "Unknown")
                error_message = data.get("msg", "Unknown error")
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"BingX API Error: [{code}] {error_message}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

            if not response.status_code // 100 == 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

            return data
