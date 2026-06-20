"""Aster V3 asynchronous HTTP manager."""

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native
from ...aster._http_manager import (
    _NATIVE_PRIVATE_REQUESTS,
    AsterPath,
    _filtered_query,
    _format_value,
)
from ...aster.endpoints.account import FuturesAccount, SpotAccount
from ...aster.endpoints.market import FuturesMarket, SpotMarket
from ...aster.endpoints.trade import FuturesTrade, SpotTrade
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


@dataclass
class HTTPManager(BaseHTTPManager):
    """Asynchronous HTTP manager for Aster V3 spot and futures APIs."""

    EXCHANGE = Common.ASTER

    user_address: str | None = field(default=None, repr=False)
    signer_address: str | None = field(default=None, repr=False)
    private_key: str | None = field(default=None, repr=False)
    spot_base_url: str = field(default="https://sapi.asterdex.com")
    futures_base_url: str = field(default="https://fapi.asterdex.com")
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: Any = field(default=None, init=False, repr=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize the asynchronous Aster HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "AsterHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                user_address=self.user_address,
                signer_address=self.signer_address,
                private_key=self.private_key,
                timeout=self.timeout,
                spot_base_url=self.spot_base_url,
                futures_base_url=self.futures_base_url,
            )
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.ASTER)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _native_response(
        self,
        method_name: str,
        params: list[tuple[str, str]],
        *,
        private: bool,
    ) -> dict[str, Any] | list[Any]:
        if self._native_client is None:
            await self.async_init()
        if self._native_client is None:
            raise RuntimeError("Aster native client is required.")
        method = "private_request_async" if private else "public_request_async"
        if not hasattr(self._native_client, method):
            raise RuntimeError(f"Aster native client {method} is unavailable.")
        request_summary = self._native_request_summary(method_name, params)
        try:
            status, headers, body = await getattr(self._native_client, method)(
                method_name,
                params,
            )
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=request_summary,
                message=str(exc),
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        return await self._native_response(method_name, params, private=False)

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        return await self._native_response(method_name, params, private=True)

    def _native_request_summary(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> str:
        if method_name == "transfer_spot_futures":
            market = dict(params).get("market", "spot").lower()
            spec = (
                "POST",
                SpotAccount.TRANSFER if market == "spot" else FuturesAccount.TRANSFER,
            )
        else:
            spec = _NATIVE_PRIVATE_REQUESTS.get(method_name)
        if spec is None:
            return f"GET {self.spot_base_url}/{method_name} | Body: {params}"
        method, path = spec
        return f"{method} {self._get_base_url(path)}{path} | Body: {params}"

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            if key == "type_":
                key = "type"
            elif key == "from_":
                key = "from"
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if (
                key == "symbols"
                and isinstance(value, Sequence)
                and not isinstance(
                    value,
                    str | bytes | bytearray,
                )
            ):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, _format_value(value)))
        return params

    def _get_base_url(self, path: AsterPath) -> str:
        if isinstance(path, SpotMarket | SpotAccount | SpotTrade):
            return self.spot_base_url
        if isinstance(path, FuturesMarket | FuturesAccount | FuturesTrade):
            return self.futures_base_url
        raise ValueError(f"Unknown Aster API path: {path} (type={type(path)})")

    async def _request(
        self,
        method: str,
        path: AsterPath,
        query: Mapping[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any] | list[Any]:
        """Make an asynchronous Aster V3 REST request."""
        if self._native_client is None:
            await self.async_init()

        method_upper = method.upper()
        include_user = isinstance(path, FuturesMarket | FuturesAccount | FuturesTrade)
        self._uses_native_transport()
        if signed:
            if not self.signer_address or not self.private_key:
                raise ValueError("Signed Aster requests require signer_address and private_key.")
            if include_user and not self.user_address:
                raise ValueError("Signed Aster futures requests require user_address.")
        params = _filtered_query(query)
        url = f"{self._get_base_url(path)}{path}"
        try:
            self._log_request(method_upper, url)
            market = "futures" if include_user else "spot"
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
                method,
                market,
                str(path),
                list(params.items()),
                signed,
            )
            response = NativeResponse(
                status,
                dict(response_headers),
                bytes(response_body),
            )
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {params}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc

        self._store_response_headers(response)
        try:
            data: dict[str, Any] | list[Any] = response.json()
        except Exception as exc:
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {params}",
                message=f"Failed to decode JSON response: {exc}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            ) from exc

        error_code = data.get("code") if isinstance(data, dict) else None
        if response.status_code // 100 != 2 or (
            error_code is not None and str(error_code) not in {"0", "200"}
        ):
            message = data.get("msg") or data.get("message") if isinstance(data, dict) else data
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {params}",
                message=f"Aster API error [{error_code}]: {message}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )
        return data

    async def close(self) -> None:
        """Close the asynchronous HTTP session."""
        if self.session is not None and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.session = None
