"""Lighter asynchronous HTTP manager."""

import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, Self
from urllib.parse import urlencode

import httpx

from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager


class _SignerClient(Protocol):
    def create_auth_token_with_expiry(
        self,
        deadline: int = -1,
        *,
        timestamp: int = 0,
        api_key_index: int = 255,
    ) -> tuple[str | None, str | None]: ...

    def check_client(self) -> str | None: ...

    def sign_create_order(
        self,
        market_index: int,
        client_order_index: int,
        base_amount: int,
        price: int,
        is_ask: bool,
        order_type: int,
        time_in_force: int,
        reduce_only: bool = False,
        trigger_price: int = 0,
        order_expiry: int = -1,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...

    def sign_cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...

    def sign_modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...

    def sign_cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...

    def sign_update_leverage(
        self,
        market_index: int,
        fraction: int,
        margin_mode: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...

    def sign_update_margin(
        self,
        market_index: int,
        usdc_amount: int,
        direction: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[Any, Any, Any, Any]: ...


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
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False, repr=False)
    _signer: _SignerClient | None = field(default=None, init=False, repr=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.LIGHTER)
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aenter__(self) -> Self:
        if self.session is None or self.session.is_closed:
            await self.async_init()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def _request(
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
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session.")

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
            if method_upper == "GET":
                response = await self.session.get(url, headers=request_headers)
            elif method_upper == "POST":
                response = await self.session.post(
                    url,
                    headers=request_headers,
                    content=request_body,
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except httpx.RequestError as exc:
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

    def _private_signer(self) -> _SignerClient:
        if self._signer is None:
            raise ValueError("Lighter local signer is not configured.")
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

    async def _signed_tx(
        self,
        result: tuple[Any, Any, Any, Any],
        *,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        tx_type, tx_info, _tx_hash, error = result
        if error is not None:
            raise ValueError(f"Lighter signing failed: {error}")
        from .endpoints.market import Public

        return await self._request(
            "POST",
            Public.SEND_TX,
            body={
                "tx_type": int(tx_type),
                "tx_info": str(tx_info),
                "price_protection": price_protection,
            },
            content_type="form",
        )

    async def close_signer(self) -> None:
        """Clear any injected Lighter signer."""
        self._signer = None

    async def close(self) -> None:
        """Close the HTTP session."""
        await self.close_signer()
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
