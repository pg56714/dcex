"""Extended asynchronous HTTP manager."""

import json
import logging
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native, native_body_text, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, Mapping) or (
        isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray)
    ):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def _env_int(name: str) -> int | None:
    value = os.getenv(name)
    if not value:
        return None
    return int(value)


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Extended REST APIs."""

    EXCHANGE = Common.EXTENDED

    base_url: str = field(default="https://api.starknet.extended.exchange")
    api_key: str | None = field(default=None, repr=False)
    stark_private_key: str | None = field(default=None, repr=False)
    stark_public_key: str | None = field(default=None, repr=False)
    vault_number: int | None = field(default=None, repr=False)
    client_id: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    user_agent: str = field(default="dcex-python/0.1")
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        self._logger = self._setup_logger(self.logger)
        self.api_key = self.api_key or os.getenv("EXTENDED_API_KEY") or None
        self.stark_private_key = (
            self.stark_private_key or os.getenv("EXTENDED_STARK_PRIVATE_KEY") or None
        )
        self.stark_public_key = (
            self.stark_public_key or os.getenv("EXTENDED_STARK_PUBLIC_KEY") or None
        )
        self.vault_number = self.vault_number or _env_int("EXTENDED_VAULT_NUMBER")
        self.client_id = self.client_id or os.getenv("EXTENDED_CLIENT_ID") or None
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.EXTENDED)
        native_client_type = getattr(_native, "ExtendedHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            try:
                self._native_client = native_client_type(
                    api_key=self.api_key,
                    stark_private_key=self.stark_private_key,
                    stark_public_key=self.stark_public_key,
                    vault_number=self.vault_number,
                    client_id=self.client_id,
                    timeout=self.timeout,
                    base_url=self.base_url,
                    user_agent=self.user_agent,
                )
            except TypeError:
                self._native_client = native_client_type(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    base_url=self.base_url,
                    user_agent=self.user_agent,
                )
        native_client = self._native_client
        if (
            self.preload_product_table
            and native_client is not None
            and hasattr(native_client, "set_product_table")
        ):
            native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            if key == "type_":
                key = "type"
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            params.append((key, _format_value(value)))
        return params

    async def _native_public(self, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        if self._native_client is None:
            await self.async_init()
        self._uses_native_transport()
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "public_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Extended {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def _native_private(self, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        if self._native_client is None:
            await self.async_init()
        self._uses_native_transport()
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Extended {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def _request(
        self,
        method: str,
        path: str,
        query: Mapping[str, Any] | None = None,
        signed: bool = False,
        body: bytes | None = None,
    ) -> Any:  # noqa: ANN401
        if self._native_client is None:
            await self.async_init()
        self._uses_native_transport()
        params = [(key, _format_value(value)) for key, value in (query or {}).items()]
        try:
            status, response_headers, data = await cast(
                Any,
                self._native_client,
            ).request_raw_json_async(method, path, params, body, signed, None)
            response = NativeResponse(status, dict(response_headers))
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {self.base_url}{path} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc
        self._store_response_headers(response)
        if response.status_code // 100 != 2:
            raise FailedRequestError(
                request=f"{method.upper()} {self.base_url}{path} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {native_body_text(data)}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )
        return data

    async def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
