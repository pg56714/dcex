# ruff: noqa: ANN401
"""Arcus HTTP implementation mixins."""

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
from ._request_params import _params


@dataclass
class HTTPManager(BaseHTTPManager):
    """Arcus perpetual manager methods."""

    EXCHANGE = Common.ARCUS

    api_key: str | None = field(default=None, repr=False)

    api_secret: str | None = field(default=None, repr=False)

    address: str | None = None

    account_index: int | None = None

    testnet: bool = False

    timeout: float = 10.0

    base_url: str | None = None

    preload_product_table: bool = False

    logger: logging.Logger | None = None

    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    def __post_init__(self) -> None:
        self._logger = self._setup_logger(self.logger)
        self.api_key = self.api_key or os.getenv("ARCUS_API_KEY") or None
        self.api_secret = self.api_secret or os.getenv("ARCUS_API_SIGNING_KEY") or None
        self.address = self.address or os.getenv("ARCUS_ADDRESS") or None
        if self.account_index is None:
            self.account_index = 0
        self._native_client = load_native().ArcusHttpClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            address=self.address,
            account_index=self.account_index,
            testnet=self.testnet,
            timeout=self.timeout,
            base_url=self.base_url,
        )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.ARCUS)
            self._native_client.set_product_table(self.ptm.product_table)

    def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        try:
            response, data = request_native_json(self._native_client, kind, method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Arcus {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    def public_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named read-only Arcus endpoint."""
        return self._call("public_request", method_name, _params(**params))

    def private_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named signed Arcus order endpoint."""
        return self._call("private_request", method_name, _params(**params))

    def close(self) -> None:
        """Release the native client."""
        self._native_client = None


@dataclass
class SpotHTTPManager(BaseHTTPManager):
    """Arcus spot manager methods."""

    EXCHANGE = Common.ARCUS

    api_key: str | None = field(default=None, repr=False)

    testnet: bool = False

    timeout: float = 10.0

    base_url: str | None = None

    wallet_address: str | None = None

    rpc_url: str | None = None

    logger: logging.Logger | None = None

    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    def __post_init__(self) -> None:
        self._logger = self._setup_logger(self.logger)
        self.wallet_address = self.wallet_address or os.getenv("ARCUS_ADDRESS")
        self._native_client = load_native().ArcusSpotHttpClient(
            api_key=self.api_key,
            testnet=self.testnet,
            timeout=self.timeout,
            base_url=self.base_url,
            wallet_address=self.wallet_address,
            rpc_url=self.rpc_url,
        )

    def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        try:
            response, data = request_native_json(self._native_client, kind, method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Arcus Spot {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    def close(self) -> None:
        """Release the native router client."""
        self._native_client = None
