"""MEXC synchronous HTTP manager."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import parse_qsl, urlencode

from .._native_http import NativeResponse, load_native, native_body_text, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp

RequestPayload = dict[str, Any] | list[Any]
_native = load_native()


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _filtered_query(query: RequestPayload | None) -> RequestPayload:
    if isinstance(query, list):
        return [
            {key: value for key, value in item.items() if value is not None}
            if isinstance(item, dict)
            else item
            for item in query
        ]
    return {key: value for key, value in (query or {}).items() if value is not None}


def _encoded_query(query: dict[str, Any], *, sort: bool = False) -> str:
    items = sorted(query.items()) if sort else query.items()
    return urlencode({key: _format_value(value) for key, value in items}, doseq=True)


def _json_body(query: RequestPayload) -> str:
    return json.dumps(query, separators=(",", ":"), ensure_ascii=False) if query else ""


def _query_pairs(query: dict[str, Any]) -> list[tuple[str, str]]:
    return parse_qsl(_encoded_query(query), keep_blank_values=True)


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for MEXC Spot V3 and Contract V1 REST APIs."""

    EXCHANGE = Common.MEXC

    base_url: str = field(default="https://api.mexc.com")
    contract_base_url: str | None = field(default=None)
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "MexcHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        self._native_client = native_client_type(
            api_key=self.api_key,
            api_secret=self.api_secret,
            timeout=self.timeout,
            base_url=self.base_url,
            contract_base_url=self.contract_base_url,
        )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.MEXC)
            if self._native_client is not None and hasattr(
                self._native_client, "set_product_table"
            ):
                self._native_client.set_product_table(self.ptm._native_table)

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed MEXC private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("MEXC native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_json"):
            raise RuntimeError("MEXC native client private_request_json is unavailable.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"MEXC {method_name} | Params: {params}",
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
            if key == "type_":
                key = "type"
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            params.append((key, str(value)))
        return params

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: RequestPayload | None = None,
        signed: bool = True,
        api: Literal["spot", "contract"] = "spot",
    ) -> dict[str, Any] | list[Any]:
        """Make an HTTP request to MEXC REST APIs."""
        request_path = str(path)
        filtered_query = _filtered_query(query)
        base_url = (self.contract_base_url or self.base_url) if api == "contract" else self.base_url
        url = f"{base_url}{request_path}"

        try:
            self._log_request(method, url)
            self._uses_native_transport()
            if signed and not (self.api_key and self.api_secret):
                raise ValueError("Signed MEXC requests require api_key and api_secret.")
            if api == "spot" and not isinstance(filtered_query, dict):
                raise TypeError("MEXC Spot requests require a mapping query.")
            params = _query_pairs(filtered_query) if isinstance(filtered_query, dict) else []
            body = None
            if api == "contract" and method.upper() not in {"GET", "DELETE"}:
                body = _json_body(filtered_query).encode()
            status, response_headers, response_body = cast(
                Any,
                self._native_client,
            ).request_raw_json(
                method,
                api,
                request_path,
                params,
                body,
                signed,
            )
            response = NativeResponse(status, dict(response_headers))
        except RuntimeError as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc

        self._store_response_headers(response)
        data = response_body
        if response.status_code // 100 != 2:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {native_body_text(data)}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )

        if isinstance(data, dict):
            code = data.get("code")
            success = data.get("success")
            if success is False or (code is not None and code not in {0, "0", 200, "200"}):
                message = data.get("msg") or data.get("message") or "Unknown error"
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"MEXC API Error: [{code}] {message}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

        return data

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
