"""Kraken synchronous HTTP manager."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import urlencode

from .._native_http import NativeResponse, load_native, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

_native = load_native()

AuthType = Literal["spot", "futures"]


def _kraken_error_message(data: Any) -> str | None:  # noqa: ANN401
    if not isinstance(data, dict):
        return None

    spot_errors = data.get("error")
    if isinstance(spot_errors, list) and spot_errors:
        return ", ".join(str(error) for error in spot_errors)
    if isinstance(spot_errors, str) and spot_errors:
        return spot_errors

    if data.get("result") == "error":
        futures_errors = data.get("errors") or data.get("error")
        if isinstance(futures_errors, list):
            return ", ".join(str(error) for error in futures_errors)
        if futures_errors:
            return str(futures_errors)
        return "Kraken API error"

    return None


def _filtered_query(query: dict[str, Any] | None) -> dict[str, Any]:
    filtered: dict[str, Any] = {}
    for key, value in (query or {}).items():
        if value is None:
            continue
        filtered[key] = str(value).lower() if isinstance(value, bool) else value
    return filtered


def _encoded_query(query: dict[str, Any]) -> str:
    return urlencode(query, doseq=True)


def _native_params(query: dict[str, Any]) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []
    for key, value in query.items():
        if isinstance(value, (list, tuple)):
            params.extend((key, str(item)) for item in value)
        else:
            params.append((key, str(value)))
    return params


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Kraken public REST APIs."""

    EXCHANGE = Common.KRAKEN

    base_url: str = field(default="https://api.kraken.com")
    futures_base_url: str = field(default="https://futures.kraken.com")
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    spot_api_key: str | None = field(default=None, repr=False)
    spot_api_secret: str | None = field(default=None, repr=False)
    futures_api_key: str | None = field(default=None, repr=False)
    futures_api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "KrakenHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        self._native_client = native_client_type(
            spot_api_key=self._spot_api_key,
            spot_api_secret=self._spot_api_secret,
            futures_api_key=self._futures_api_key,
            futures_api_secret=self._futures_api_secret,
            timeout=self.timeout,
            spot_base_url=self.base_url,
            futures_base_url=self.futures_base_url,
        )

        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.KRAKEN)
            if self._native_client is not None:
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    @property
    def _spot_api_key(self) -> str | None:
        return self.spot_api_key or self.api_key

    @property
    def _spot_api_secret(self) -> str | None:
        return self.spot_api_secret or self.api_secret

    @property
    def _futures_api_key(self) -> str | None:
        return self.futures_api_key or self.api_key

    @property
    def _futures_api_secret(self) -> str | None:
        return self.futures_api_secret or self.api_secret

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Kraken private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Kraken native client is required for private methods.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"KRAKEN {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == "from_":
                key = "from"
            elif key == "type_":
                key = "type"
            elif key == "fee_info":
                key = "fee-info"
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            if isinstance(value, (list, tuple)):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, str(value)))
        return params

    def _infer_auth_type(self, path: str, base_url: str | None) -> AuthType:
        if path.startswith("/derivatives") or base_url == self.futures_base_url:
            return "futures"
        return "spot"

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = False,
        base_url: str | None = None,
        auth_type: AuthType | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to Kraken REST APIs."""
        request_path = str(path)
        filtered_query = _filtered_query(query)
        selected_auth_type = auth_type or self._infer_auth_type(request_path, base_url)
        encoded_query = _encoded_query(filtered_query)
        request_base_url = base_url or self.base_url

        if filtered_query:
            request_path = f"{request_path}?{encoded_query}"

        url = f"{request_base_url}{request_path}"
        try:
            self._log_request(method, url)
            method_upper = method.upper()
            if signed and selected_auth_type == "spot" and method_upper != "POST":
                raise ValueError("Signed Kraken spot requests must use POST.")
            if (
                signed
                and selected_auth_type == "spot"
                and not (self._spot_api_key and self._spot_api_secret)
            ):
                raise ValueError(
                    "Signed Kraken spot requests require spot_api_key and spot_api_secret."
                )
            if (
                signed
                and selected_auth_type == "futures"
                and not (self._futures_api_key and self._futures_api_secret)
            ):
                raise ValueError(
                    "Signed Kraken futures requests require futures_api_key and futures_api_secret."
                )

            self._uses_native_transport()
            json_body = (
                json.dumps(filtered_query, separators=(",", ":")).encode()
                if method_upper in {"POST", "PUT"} and filtered_query and not signed
                else None
            )
            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw(
                method,
                selected_auth_type,
                str(path),
                _native_params(filtered_query),
                json_body,
                signed,
            )
            response = NativeResponse(
                status,
                dict(response_headers),
                bytes(response_body),
            )
        except RuntimeError as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {e}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from e
        else:
            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                ) from exc

            timestamp = str(generate_timestamp(iso_format=True))
            error_message = _kraken_error_message(data)
            if error_message:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"KRAKEN API Error: {error_message}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                )

            if response.status_code // 100 != 2:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=timestamp,
                    resp_headers=dict(response.headers),
                )

            return data

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
