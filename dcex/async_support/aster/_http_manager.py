"""Aster V3 asynchronous HTTP manager."""

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native, request_native_json_async
from ...aster._http_manager import (
    _filtered_query,
    _format_value,
)
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
        method = "private_request" if private else "public_request"
        json_method = f"{method}_json_async"
        if not hasattr(self._native_client, json_method):
            raise RuntimeError(f"Aster native client {json_method} is unavailable.")
        request_summary = self._native_request_summary(method_name, params)
        try:
            response, data = await request_native_json_async(
                self._native_client,
                method,
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
        self._store_response_headers(response)
        return data

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
        return f"ASTER {method_name} | Params: {params}"

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

    async def _request(
        self,
        method: str,
        path: str,
        query: Mapping[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any] | list[Any]:
        """Make an asynchronous Aster V3 REST request."""
        if self._native_client is None:
            await self.async_init()

        method_upper = method.upper()
        self._uses_native_transport()
        params = _filtered_query(query)
        request_path = str(path)
        url = request_path
        try:
            self._log_request(method_upper, url)
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_auto_json_async(
                method,
                request_path,
                list(params.items()),
                signed,
            )
            response = NativeResponse(status, dict(response_headers))
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
        data = response_body
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
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
