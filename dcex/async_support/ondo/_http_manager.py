"""Asynchronous Ondo REST manager backed by the Rust extension."""

# ruff: noqa: ANN401

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Self

from ..._native_http import load_native, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...ondo._http_manager import _params
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


@dataclass
class HTTPManager(BaseHTTPManager):
    """Ondo async connection and optional product symbol translation."""

    EXCHANGE = Common.ONDO
    base_url: str = "https://api.ondoperps.xyz"
    api_key_id: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: float = 10.0
    preload_product_table: bool = False
    logger: logging.Logger | None = None
    ptm: ProductTableManager | None = field(default=None, init=False)
    _native_client: Any = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        self._logger = self._setup_logger(self.logger)
        self.api_key_id = self.api_key_id or os.getenv("ONDO_API_KEY_ID") or None
        self.api_secret = self.api_secret or os.getenv("ONDO_API_SECRET") or None
        if self._native_client is None:
            self._native_client = load_native().OndoHttpClient(
                api_key_id=self.api_key_id,
                api_secret=self.api_secret,
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.ONDO)
            self._native_client.set_product_table(self.ptm._native_table)
        return self

    async def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:
        if self._native_client is None:
            await self.async_init()
        try:
            response, data = await request_native_json_async(
                self._native_client,
                kind,
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Ondo {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def _native_public(self, method_name: str, **kwargs: object) -> Any:
        return await self._call("public_request", method_name, _params(**kwargs))

    async def _native_private(self, method_name: str, **kwargs: object) -> Any:
        return await self._call("private_request", method_name, _params(**kwargs))

    async def public_request(self, method_name: str, **params: object) -> Any:
        return await self._native_public(method_name, **params)

    async def private_request(self, method_name: str, **params: object) -> Any:
        return await self._native_private(method_name, **params)

    async def close(self) -> None:
        self._native_client = None
