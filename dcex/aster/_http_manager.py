"""Aster V3 synchronous HTTP manager."""

import json
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from .._native_http import NativeResponse, load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()


def sign_message(message: str, private_key: str) -> str:
    """Sign an Aster V3 EIP-712 message using the Rust native extension."""
    if not hasattr(_native, "aster_sign_message"):
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
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the Aster HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "AsterHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
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
        if self._native_client is None:
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

    def _request(
        self,
        method: str,
        path: str,
        query: Mapping[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any] | list[Any]:
        """Make an Aster V3 REST request."""
        method_upper = method.upper()
        self._uses_native_transport()
        params = _filtered_query(query)
        request_path = str(path)
        url = request_path
        try:
            self._log_request(method_upper, url)
            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw_auto(
                method,
                request_path,
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

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and hasattr(self.session, "close"):
            self.session.close()
        self.session = None
