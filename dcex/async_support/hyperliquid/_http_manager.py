"""HTTP manager for Hyperliquid exchange API with optimized authentication and request handling."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Self, cast

from ..._native_http import NativeResponse, load_native, request_native_json_async
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()

HTTP_URL = "https://{SUBDOMAIN}.{DOMAIN}.{TLD}"
SUBDOMAIN_MAIN = "api"
DOMAIN_MAINNET = "hyperliquid"
DOMAIN_TESTNET = "hyperliquid-testnet"
TLD_MAIN = "xyz"


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    HTTP manager for Hyperliquid exchange API with optimized authentication and request handling.

    This class provides high-performance HTTP client functionality backed by
    Rust native cryptographic operations.
    """

    EXCHANGE = Common.HYPERLIQUID

    testnet: bool = field(default=False)
    subdomain: str = field(default=SUBDOMAIN_MAIN)
    tld: str = field(default=TLD_MAIN)
    wallet_address: str | None = field(default=None)
    private_key: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    ptm: ProductTableManager | None = field(init=False, default=None)
    preload_product_table: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Returns:
            Self for method chaining
        """
        self._logger = self._setup_logger(self.logger)
        ptm: ProductTableManager | None = None
        if self.preload_product_table:
            ptm = await ProductTableManager.get_instance(Common.HYPERLIQUID)
            self.ptm = ptm
        domain = DOMAIN_TESTNET if self.testnet else DOMAIN_MAINNET
        self.endpoint = HTTP_URL.format(SUBDOMAIN=self.subdomain, DOMAIN=domain, TLD=self.tld)
        native_client_type = getattr(_native, "HyperliquidHttpClient", None)
        if native_client_type is None:
            raise RuntimeError("The dcex native extension is required.")
        if self._native_client is None:
            self._native_client = native_client_type(
                testnet=self.testnet,
                wallet_address=self.wallet_address,
                private_key=self.private_key,
                timeout=self.timeout,
                endpoint=self.endpoint,
            )
        if (
            self.preload_product_table
            and self._native_client is not None
            and hasattr(self._native_client, "set_product_table")
            and ptm is not None
        ):
            self._native_client.set_product_table(ptm._native_table)
        return self

    def _uses_native_transport(self) -> bool:
        if self._native_client is None:
            raise RuntimeError(
                "The dcex native extension is required; Python HTTP fallback has been removed."
            )
        return True

    async def _get_ptm(self) -> ProductTableManager:
        """Lazily obtain the product table manager instance."""
        ptm = self.ptm
        if ptm is None:
            ptm = await ProductTableManager.get_instance(Common.HYPERLIQUID)
            self.ptm = ptm
            if self._native_client is not None and hasattr(
                self._native_client,
                "set_product_table",
            ):
                self._native_client.set_product_table(ptm._native_table)
        return ptm

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Hyperliquid public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Hyperliquid native client is required for public methods.")
        if not hasattr(self._native_client, "public_request_async"):
            raise RuntimeError("Hyperliquid native client public_request_async is unavailable.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "public_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"HYPERLIQUID {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Hyperliquid private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Hyperliquid native client is required for private methods.")
        if not hasattr(self._native_client, "private_request_async"):
            raise RuntimeError("Hyperliquid native client private_request_async is unavailable.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"HYPERLIQUID {method_name} | Params: {params}",
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
            if key == "self" or value is None:
                continue
            enum_value = getattr(value, "value", None)
            if enum_value is not None:
                value = enum_value
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, (list, dict)):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to the API.

        Args:
            method: HTTP method (GET, POST)
            path: API path
            query: Query parameters
            signed: Whether to sign the request

        Returns:
            Response data as dictionary

        Raises:
            ValueError: If session not initialized or unsupported method
            FailedRequestError: If request fails
        """
        if self._native_client is None:
            await self.async_init()

        query = dict(query or {})

        timestamp = int(generate_timestamp())
        self._uses_native_transport()

        if signed:
            if not (self.wallet_address and self.private_key):
                raise ValueError("Signed request requires Address and Private Key of wallet.")

        url = self.endpoint + path
        self._log_request(method, url)

        try:
            action_msgpack = None
            status, response_headers, response_body = await cast(
                Any,
                self._native_client,
            ).request_raw_async(
                method,
                path,
                json.dumps(query, separators=(",", ":")).encode(),
                action_msgpack,
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
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
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
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                ) from exc

            if not response.status_code // 100 == 2:
                self._log_failed_request(
                    f"HTTP Error {response.status_code}: {response.text}", response.status_code
                )
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data

    async def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
