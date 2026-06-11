"""Aster V3 asynchronous HTTP manager."""

import logging
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Self
from urllib.parse import urlencode

import httpx

from ...aster._http_manager import AsterPath, _filtered_query, sign_message
from ...aster.endpoints.account import FuturesAccount, SpotAccount
from ...aster.endpoints.market import FuturesMarket, SpotMarket
from ...aster.endpoints.trade import FuturesTrade, SpotTrade
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


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
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _nonce_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _last_nonce: int = field(default=0, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize the asynchronous Aster HTTP manager."""
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.ASTER)
        return self

    def _get_base_url(self, path: AsterPath) -> str:
        if isinstance(path, SpotMarket | SpotAccount | SpotTrade):
            return self.spot_base_url
        if isinstance(path, FuturesMarket | FuturesAccount | FuturesTrade):
            return self.futures_base_url
        raise ValueError(f"Unknown Aster API path: {path} (type={type(path)})")

    def _next_nonce(self) -> int:
        with self._nonce_lock:
            nonce = int(time.time_ns() // 1_000)
            if nonce <= self._last_nonce:
                nonce = self._last_nonce + 1
            self._last_nonce = nonce
            return nonce

    def _signed_query(
        self,
        query: Mapping[str, Any] | None,
        *,
        include_user: bool,
    ) -> dict[str, str]:
        if not self.signer_address or not self.private_key:
            raise ValueError("Signed Aster requests require signer_address and private_key.")
        if include_user and not self.user_address:
            raise ValueError("Signed Aster futures requests require user_address.")
        params = _filtered_query(query)
        params["nonce"] = str(self._next_nonce())
        if include_user:
            params["user"] = str(self.user_address)
        params["signer"] = self.signer_address
        message = urlencode(params)
        params["signature"] = sign_message(message, self.private_key)
        return params

    async def _request(
        self,
        method: str,
        path: AsterPath,
        query: Mapping[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any] | list[Any]:
        """Make an asynchronous Aster V3 REST request."""
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize Aster HTTP session.")

        method_upper = method.upper()
        include_user = isinstance(path, FuturesMarket | FuturesAccount | FuturesTrade)
        params = (
            self._signed_query(query, include_user=include_user)
            if signed
            else _filtered_query(query)
        )
        url = f"{self._get_base_url(path)}{path}"
        headers = {"Accept": "application/json"}
        if method_upper != "GET":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = None
        try:
            self._log_request(method_upper, url)
            if method_upper == "GET":
                response = await self.session.get(url, params=params, headers=headers)
            else:
                response = await self.session.request(
                    method_upper,
                    url,
                    data=params,
                    headers=headers,
                )
        except httpx.RequestError as exc:
            raise FailedRequestError(
                request=f"{method_upper} {url} | Body: {params}",
                message=f"Request failed: {exc}",
                status_code=response.status_code if response else "Unknown",
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers) if response else None,
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
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
        self.session = None
