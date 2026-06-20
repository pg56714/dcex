"""Aster V3 synchronous HTTP manager."""

import json
import logging
import threading
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast
from urllib.parse import urlencode

from .._native_http import NativeResponse, load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .endpoints.account import FuturesAccount, SpotAccount
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade

_native = load_native()

AsterPath = SpotMarket | FuturesMarket | SpotAccount | FuturesAccount | SpotTrade | FuturesTrade

_NATIVE_PRIVATE_REQUESTS: dict[str, tuple[str, AsterPath]] = {
    "get_spot_account": ("GET", SpotAccount.ACCOUNT),
    "get_spot_transaction_history": ("GET", SpotAccount.TRANSACTION_HISTORY),
    "get_futures_position_mode": ("GET", FuturesAccount.POSITION_MODE),
    "set_futures_position_mode": ("POST", FuturesAccount.POSITION_MODE),
    "get_futures_stp_mode": ("GET", FuturesAccount.STP_MODE),
    "set_futures_stp_mode": ("POST", FuturesAccount.STP_MODE),
    "get_futures_multi_assets_mode": ("GET", FuturesAccount.MULTI_ASSETS_MODE),
    "set_futures_multi_assets_mode": ("POST", FuturesAccount.MULTI_ASSETS_MODE),
    "get_futures_balance": ("GET", FuturesAccount.BALANCE),
    "get_futures_account": ("GET", FuturesAccount.ACCOUNT),
    "modify_futures_position_margin": ("POST", FuturesAccount.POSITION_MARGIN),
    "get_futures_position_margin_history": (
        "GET",
        FuturesAccount.POSITION_MARGIN_HISTORY,
    ),
    "get_futures_position_risk": ("GET", FuturesAccount.POSITION_RISK),
    "get_futures_user_trades": ("GET", FuturesAccount.USER_TRADES),
    "get_futures_income": ("GET", FuturesAccount.INCOME),
    "get_futures_leverage_bracket": ("GET", FuturesAccount.LEVERAGE_BRACKET),
    "get_futures_adl_quantile": ("GET", FuturesAccount.ADL_QUANTILE),
    "get_futures_force_orders": ("GET", FuturesAccount.FORCE_ORDERS),
    "get_spot_commission_rate": ("GET", SpotMarket.COMMISSION_RATE),
    "get_futures_commission_rate": ("GET", FuturesAccount.COMMISSION_RATE),
    "update_futures_mmp": ("POST", FuturesAccount.MMP),
    "get_futures_mmp": ("GET", FuturesAccount.MMP),
    "delete_futures_mmp": ("DELETE", FuturesAccount.MMP),
    "reset_futures_mmp": ("POST", FuturesAccount.MMP_RESET),
    "create_spot_listen_key": ("POST", SpotAccount.LISTEN_KEY),
    "keep_alive_spot_listen_key": ("PUT", SpotAccount.LISTEN_KEY),
    "close_spot_listen_key": ("DELETE", SpotAccount.LISTEN_KEY),
    "create_futures_listen_key": ("POST", FuturesAccount.LISTEN_KEY),
    "keep_alive_futures_listen_key": ("PUT", FuturesAccount.LISTEN_KEY),
    "close_futures_listen_key": ("DELETE", FuturesAccount.LISTEN_KEY),
    "place_spot_order": ("POST", SpotTrade.ORDER),
    "cancel_spot_order": ("DELETE", SpotTrade.ORDER),
    "get_spot_order": ("GET", SpotTrade.ORDER),
    "get_spot_open_order": ("GET", SpotTrade.OPEN_ORDER),
    "get_spot_open_orders": ("GET", SpotTrade.OPEN_ORDERS),
    "cancel_all_spot_open_orders": ("DELETE", SpotTrade.ALL_OPEN_ORDERS),
    "get_spot_all_orders": ("GET", SpotTrade.ALL_ORDERS),
    "get_spot_user_trades": ("GET", SpotTrade.USER_TRADES),
    "place_futures_order": ("POST", FuturesTrade.ORDER),
    "modify_futures_order": ("PUT", FuturesTrade.ORDER),
    "place_futures_chase_order": ("POST", FuturesTrade.CHASE),
    "place_futures_batch_orders": ("POST", FuturesTrade.BATCH_ORDERS),
    "get_futures_order": ("GET", FuturesTrade.ORDER),
    "cancel_futures_order": ("DELETE", FuturesTrade.ORDER),
    "cancel_all_futures_open_orders": ("DELETE", FuturesTrade.ALL_OPEN_ORDERS),
    "cancel_futures_batch_orders": ("DELETE", FuturesTrade.BATCH_ORDERS),
    "set_futures_countdown_cancel_all": ("POST", FuturesTrade.COUNTDOWN_CANCEL_ALL),
    "get_futures_open_order": ("GET", FuturesTrade.OPEN_ORDER),
    "get_futures_open_orders": ("GET", FuturesTrade.OPEN_ORDERS),
    "get_futures_all_orders": ("GET", FuturesTrade.ALL_ORDERS),
    "set_futures_leverage": ("POST", FuturesTrade.LEVERAGE),
    "set_futures_margin_type": ("POST", FuturesTrade.MARGIN_TYPE),
    "place_futures_strategy_order": ("POST", FuturesTrade.PLACE_STRATEGY_ORDER),
    "update_futures_strategy_order": ("POST", FuturesTrade.UPDATE_STRATEGY_ORDER),
    "get_futures_strategy_open_order": ("GET", FuturesTrade.STRATEGY_OPEN_ORDER),
    "get_futures_strategy_history_order": ("GET", FuturesTrade.STRATEGY_HISTORY_ORDER),
}


def _eip712_digest(message: str) -> bytes:
    """Reject the removed Python Aster signing fallback."""
    raise RuntimeError("Aster Python signing fallback has been removed; use Rust native signing.")


def sign_message(message: str, private_key: str) -> str:
    """Sign an Aster V3 EIP-712 message using the Rust native extension."""
    if _native is None or not hasattr(_native, "aster_sign_message"):
        raise RuntimeError("Aster native signing is required.")
    return str(_native.aster_sign_message(message, private_key))


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list | dict):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def _filtered_query(query: Mapping[str, Any] | None) -> dict[str, str]:
    return {key: _format_value(value) for key, value in (query or {}).items() if value is not None}


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Aster V3 spot and futures APIs."""

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
    _nonce_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _last_nonce: int = field(default=0, init=False, repr=False)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the Aster HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "AsterHttpClient", None)
        if self.use_native and native_client_type is not None:
            self._native_client = native_client_type(
                user_address=self.user_address,
                signer_address=self.signer_address,
                private_key=self.private_key,
                timeout=self.timeout,
                spot_base_url=self.spot_base_url,
                futures_base_url=self.futures_base_url,
            )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.ASTER)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if not self.use_native or self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _native_response(
        self,
        method_name: str,
        params: list[tuple[str, str]],
        *,
        private: bool,
    ) -> dict[str, Any] | list[Any]:
        if self._native_client is None:
            raise RuntimeError("Aster native client is required.")
        method = "private_request" if private else "public_request"
        if not hasattr(self._native_client, method):
            raise RuntimeError(f"Aster native client {method} is unavailable.")
        request_summary = self._native_request_summary(method_name, params)
        try:
            status, headers, body = getattr(self._native_client, method)(method_name, params)
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

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        return self._native_response(method_name, params, private=False)

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        return self._native_response(method_name, params, private=True)

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

    def _request(
        self,
        method: str,
        path: AsterPath,
        query: Mapping[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any] | list[Any]:
        """Make an Aster V3 REST request."""
        method_upper = method.upper()
        include_user = isinstance(path, FuturesMarket | FuturesAccount | FuturesTrade)
        uses_native = self._uses_native_transport()
        if signed and uses_native:
            if not self.signer_address or not self.private_key:
                raise ValueError("Signed Aster requests require signer_address and private_key.")
            if include_user and not self.user_address:
                raise ValueError("Signed Aster futures requests require user_address.")
        params = (
            _filtered_query(query)
            if uses_native
            else (
                self._signed_query(query, include_user=include_user)
                if signed
                else _filtered_query(query)
            )
        )
        url = f"{self._get_base_url(path)}{path}"
        headers = {"Accept": "application/json"}
        if method_upper != "GET":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = None
        try:
            self._log_request(method_upper, url)
            if uses_native:
                market = "futures" if include_user else "spot"
                status, response_headers, response_body = cast(
                    Any,
                    self._native_client,
                ).request_raw(
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
            elif method_upper == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            elif method_upper == "POST":
                response = self.session.post(
                    url,
                    data=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            elif method_upper == "PUT":
                response = self.session.put(
                    url,
                    data=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            elif method_upper == "DELETE":
                response = self.session.delete(
                    url,
                    data=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
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

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and hasattr(self.session, "close"):
            self.session.close()
        self.session = None
