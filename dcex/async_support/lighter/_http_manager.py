"""Lighter asynchronous HTTP manager backed by the Rust core."""

import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Self, cast
from urllib.parse import urlencode

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

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
    ptm: ProductTableManager | None = field(init=False, default=None, repr=False)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        self._logger = self._setup_logger(self.logger)
        native_client_type = getattr(_native, "LighterHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                timeout=self.timeout,
                base_url=self.base_url,
                account_index=self.account_index,
                api_key_index=self.api_key_index,
                api_private_key=self.api_private_key,
            )
        if self.preload_product_table and self.ptm is None:
            self.ptm = await ProductTableManager.get_instance(Common.LIGHTER)
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(self.ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def __aenter__(self) -> Self:
        if self._native_client is None:
            await self.async_init()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    @staticmethod
    def _native_params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            params.append((key, _format_value(value)))
        return params

    async def _native_call(
        self,
        method_name: str,
        params: list[tuple[str, str]],
        private: bool,
    ) -> dict[str, Any] | list[Any]:
        """Call a Rust-backed Lighter method and decode its JSON body."""
        if self._native_client is None:
            await self.async_init()
        native_client = self._native_client
        method = "private_request_async" if private else "public_request_async"
        if native_client is None or not hasattr(native_client, method):
            raise RuntimeError(f"Lighter native client {method} is unavailable.")
        try:
            status, headers, body = await getattr(native_client, method)(method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"LIGHTER {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        """Call a Rust-backed Lighter public method."""
        return await self._native_call(method_name, params, private=False)

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> dict[str, Any] | list[Any]:
        """Call a Rust-backed Lighter private method."""
        return await self._native_call(method_name, params, private=True)

    async def _native_sign(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter transaction via Rust."""
        if self._native_client is None:
            await self.async_init()
        native_client = self._native_client
        if native_client is not None and hasattr(native_client, "sign_request_async"):
            return cast(
                tuple[Any, Any, Any, Any],
                await native_client.sign_request_async(method_name, params),
            )
        raise RuntimeError("Lighter native client sign_request_async is unavailable.")

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
        """Make a raw HTTP request to Lighter REST APIs."""
        if signed:
            raise ValueError("Signed raw Lighter requests are not implemented; use native methods.")
        if self._native_client is None:
            await self.async_init()

        request_path = str(path)
        filtered_query = _filtered_query(query)
        url = f"{self.base_url}{request_path}"
        query_string = _encoded_query(filtered_query)
        if query_string:
            url = f"{url}?{query_string}"

        try:
            self._log_request(method, url)
            self._uses_native_transport()
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
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

    def _auth_token(
        self,
        authorization: str | None = None,
        *,
        deadline: int | None = None,
        api_key_index: int | None = None,
    ) -> str:
        if authorization:
            return authorization
        native_client = self._native_client
        if native_client is not None and hasattr(native_client, "create_auth_token"):
            return str(native_client.create_auth_token(deadline, api_key_index))
        raise RuntimeError("Lighter native client create_auth_token is unavailable.")

    async def _native_check_client(self) -> str | None:
        if self._native_client is None:
            await self.async_init()
        native_client = self._native_client
        if native_client is not None and hasattr(native_client, "check_client_async"):
            return cast(str | None, await native_client.check_client_async())
        raise RuntimeError("Lighter native client check_client_async is unavailable.")

    async def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
