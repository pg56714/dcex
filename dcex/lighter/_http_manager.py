"""Lighter synchronous HTTP manager."""

import logging
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import urlencode

import requests

from .._native_http import NativeResponse, load_native
from ..base.http_manager import BaseHTTPManager
from ..product_table.manager import ProductTableManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .signer_client import SignerClient

_native = load_native()


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _filtered_query(query: dict[str, Any] | None) -> dict[str, Any]:
    return {key: value for key, value in (query or {}).items() if value is not None}


def _encoded_query(query: dict[str, Any]) -> str:
    return urlencode({key: _format_value(value) for key, value in query.items()}, doseq=True)


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for Lighter REST APIs."""

    EXCHANGE = Common.LIGHTER

    base_url: str = field(default="https://mainnet.zklighter.elliot.ai")
    account_index: int | None = field(default=None)
    api_key_index: int | None = field(default=None)
    api_private_key: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: requests.Session = field(default_factory=requests.Session, init=False)
    ptm: ProductTableManager = field(init=False, repr=False)
    _signer: SignerClient | None = field(default=None, init=False, repr=False)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize sync HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "LighterHttpClient", None)
        if self.use_native and native_client_type is not None:
            self._native_client = native_client_type(
                timeout=self.timeout,
                base_url=self.base_url,
            )
        if self.preload_product_table:
            self.ptm = ProductTableManager.get_instance(Common.LIGHTER)

    def _uses_native_transport(self) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is requests.Session
        )

    def _request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        signed: bool = False,
        headers: dict[str, str] | None = None,
        content_type: Literal["json", "form"] = "json",
    ) -> dict[str, Any] | list[Any]:
        """Make an HTTP request to Lighter REST APIs."""
        if signed:
            raise ValueError("Signed Lighter requests are not implemented yet.")

        request_path = str(path)
        filtered_query = _filtered_query(query)
        url = f"{self.base_url}{request_path}"
        query_string = _encoded_query(filtered_query)
        if query_string:
            url = f"{url}?{query_string}"

        request_headers = {
            "Content-Type": (
                "application/x-www-form-urlencoded"
                if content_type == "form"
                else "application/json"
            )
        }
        request_headers.update({key: value for key, value in (headers or {}).items() if value})
        request_body = _encoded_query(_filtered_query(body)) if body else None

        response = None
        try:
            self._log_request(method, url)
            method_upper = method.upper()
            if self._uses_native_transport():
                status, response_headers, response_body = cast(
                    Any,
                    self._native_client,
                ).request_raw(
                    method,
                    request_path,
                    [(key, _format_value(value)) for key, value in filtered_query.items()],
                    [(key, _format_value(value)) for key, value in _filtered_query(body).items()],
                    signed,
                    {key: value for key, value in (headers or {}).items() if value},
                    content_type,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            elif method_upper == "GET":
                response = self.session.get(url, headers=request_headers, timeout=self.timeout)
            elif method_upper == "POST":
                response = self.session.post(
                    url,
                    headers=request_headers,
                    data=request_body,
                    timeout=self.timeout,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except (requests.RequestException, RuntimeError) as exc:
            status_code, resp_headers = self._exception_response_details(exc)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=resp_headers,
            ) from exc

        self._store_response_headers(response)
        if response.status_code // 100 != 2:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {response.text}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )

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

        if isinstance(data, dict):
            code = data.get("code")
            if code is not None and code not in {0, "0", 200, "200"}:
                message = data.get("message") or data.get("msg") or "Unknown error"
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Lighter API Error: [{code}] {message}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

        return data

    def _private_account_index(self, account_index: int | None = None) -> int:
        resolved = self.account_index if account_index is None else account_index
        if resolved is None:
            raise ValueError("Lighter private requests require account_index.")
        return int(resolved)

    def _private_api_key_index(self, api_key_index: int | None = None) -> int:
        resolved = self.api_key_index if api_key_index is None else api_key_index
        if resolved is None:
            raise ValueError("Lighter private requests require api_key_index.")
        return int(resolved)

    def _private_signer(self) -> SignerClient:
        account_index = self._private_account_index()
        api_key_index = self._private_api_key_index()
        api_private_key = self.api_private_key
        if not api_private_key:
            raise ValueError("Lighter private requests require api_private_key.")
        if self._signer is None:
            self._signer = SignerClient(
                url=self.base_url,
                account_index=account_index,
                api_private_keys={api_key_index: api_private_key},
            )
        return self._signer

    def _auth_token(
        self,
        authorization: str | None = None,
        *,
        deadline: int | None = None,
        api_key_index: int | None = None,
    ) -> str:
        if authorization:
            return authorization
        signer = self._private_signer()
        kwargs: dict[str, int] = {"api_key_index": self._private_api_key_index(api_key_index)}
        if deadline is not None:
            kwargs["deadline"] = deadline
        token, error = signer.create_auth_token_with_expiry(**kwargs)
        if error is not None:
            raise ValueError(f"Lighter auth token creation failed: {error}")
        if token is None:
            raise ValueError("Lighter auth token creation returned no token.")
        return token

    def _signed_tx(
        self,
        result: tuple[Any, Any, Any, Any],
        *,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        tx_type, tx_info, _tx_hash, error = result
        if error is not None:
            raise ValueError(f"Lighter signing failed: {error}")
        from .endpoints.market import Public

        return self._request(
            "POST",
            Public.SEND_TX,
            body={
                "tx_type": int(tx_type),
                "tx_info": str(tx_info),
                "price_protection": price_protection,
            },
            content_type="form",
        )

    def close_signer(self) -> None:
        """Close the Lighter signer client if it was initialized."""
        signer = self._signer
        self._signer = None
        if signer is not None:
            signer.close()

    def close(self) -> None:
        """Close the HTTP session."""
        self.close_signer()
        self.session.close()
