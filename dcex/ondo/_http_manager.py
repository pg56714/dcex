"""Synchronous Ondo Perps REST manager backed by the Rust extension."""

# ruff: noqa: ANN401

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from .._native_http import load_native, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp


def _params(**kwargs: object) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for key, value in kwargs.items():
        if value is None:
            continue
        key = {
            "from_time": "from",
            "to_time": "to",
            "range_": "range",
            "from_wallet": "from",
        }.get(key, key)
        if isinstance(value, bool):
            encoded = str(value).lower()
        elif isinstance(value, dict | list | tuple):
            encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        else:
            encoded = str(getattr(value, "value", value))
        result.append((key, encoded))
    return result


@dataclass
class HTTPManager(BaseHTTPManager):
    """Ondo HTTP connection and optional product symbol translation."""

    EXCHANGE = Common.ONDO
    base_url: str = "https://api.ondoperps.xyz"
    api_key_id: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: float = 10.0
    preload_product_table: bool = False
    logger: logging.Logger | None = None
    ptm: ProductTableManager | None = field(default=None, init=False)
    _native_client: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._logger = self._setup_logger(self.logger)
        self.api_key_id = self.api_key_id or os.getenv("ONDO_API_KEY_ID") or None
        self.api_secret = self.api_secret or os.getenv("ONDO_API_SECRET") or None
        self._native_client = load_native().OndoHttpClient(
            api_key_id=self.api_key_id,
            api_secret=self.api_secret,
            timeout=self.timeout,
            base_url=self.base_url,
        )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.ONDO)
            self._native_client.set_product_table(self.ptm._native_table)

    def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:
        try:
            response, data = request_native_json(self._native_client, kind, method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Ondo {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    def _native_public(self, method_name: str, **kwargs: object) -> Any:
        return self._call("public_request", method_name, _params(**kwargs))

    def _native_private(self, method_name: str, **kwargs: object) -> Any:
        return self._call("private_request", method_name, _params(**kwargs))

    def public_request(self, method_name: str, **params: object) -> Any:
        """Call a named public Ondo endpoint."""
        return self._native_public(method_name, **params)

    def private_request(self, method_name: str, **params: object) -> Any:
        """Call a named authenticated Ondo endpoint."""
        return self._native_private(method_name, **params)

    def close(self) -> None:
        self._native_client = None
