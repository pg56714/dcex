"""Aster V3 synchronous HTTP manager."""

import json
import logging
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import requests
from coincurve import PrivateKey
from Crypto.Hash import keccak

from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .endpoints.account import FuturesAccount, SpotAccount
from .endpoints.market import FuturesMarket, SpotMarket
from .endpoints.trade import FuturesTrade, SpotTrade

AsterPath = SpotMarket | FuturesMarket | SpotAccount | FuturesAccount | SpotTrade | FuturesTrade

_DOMAIN_NAME = "AsterSignTransaction"
_DOMAIN_VERSION = "1"
_DOMAIN_CHAIN_ID = 1666
_ZERO_ADDRESS = bytes(20)
_DOMAIN_TYPE = "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
_MESSAGE_TYPE = "Message(string msg)"


def _keccak(data: bytes) -> bytes:
    digest = keccak.new(digest_bits=256)
    digest.update(data)
    return digest.digest()


def _uint256(value: int) -> bytes:
    return value.to_bytes(32, "big")


def _address(value: bytes) -> bytes:
    return value.rjust(32, b"\0")


def _domain_separator() -> bytes:
    return _keccak(
        _keccak(_DOMAIN_TYPE.encode())
        + _keccak(_DOMAIN_NAME.encode())
        + _keccak(_DOMAIN_VERSION.encode())
        + _uint256(_DOMAIN_CHAIN_ID)
        + _address(_ZERO_ADDRESS)
    )


def _eip712_digest(message: str) -> bytes:
    struct_hash = _keccak(_keccak(_MESSAGE_TYPE.encode()) + _keccak(message.encode()))
    return _keccak(b"\x19\x01" + _domain_separator() + struct_hash)


def sign_message(message: str, private_key: str) -> str:
    """Sign an Aster V3 EIP-712 message and return an Ethereum signature."""
    key_hex = private_key.removeprefix("0x")
    recoverable = PrivateKey(bytes.fromhex(key_hex)).sign_recoverable(
        _eip712_digest(message),
        hasher=None,
    )
    signature = recoverable[:64] + bytes([recoverable[64] + 27])
    return f"0x{signature.hex()}"


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
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _nonce_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _last_nonce: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the Aster HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.ASTER)

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
        except requests.RequestException as exc:
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

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
