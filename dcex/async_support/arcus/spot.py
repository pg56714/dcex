"""Asynchronous Arcus spot RFQ router client."""

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Self

from ..._native_http import load_native, request_native_json_async
from ...arcus.client import _params
from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp


@dataclass
class SpotClient(BaseHTTPManager):
    """Arcus spot RFQ router; independent of the perpetuals client."""

    EXCHANGE = Common.ARCUS
    api_key: str | None = field(default=None, repr=False)
    testnet: bool = False
    timeout: float = 10.0
    base_url: str | None = None
    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    async def async_init(self) -> Self:
        """Initialize the native spot router client."""
        prefix = "ARCUS_SPOT_TESTNET" if self.testnet else "ARCUS_SPOT_MAINNET"
        self.api_key = self.api_key or os.getenv(f"{prefix}_API_KEY") or None
        self._native_client = load_native().ArcusSpotHttpClient(
            api_key=self.api_key,
            testnet=self.testnet,
            timeout=self.timeout,
            base_url=self.base_url,
        )
        return self

    async def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        if self._native_client is None:
            await self.async_init()
        try:
            response, data = await request_native_json_async(
                self._native_client, kind, method_name, params
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Arcus Spot {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def health(self) -> Any:  # noqa: ANN401
        """Get the router's unversioned health status."""
        return await self._call("public_request", "health", [])

    async def get_tokens(self) -> Any:  # noqa: ANN401
        """Get supported spot tokens and their on-chain addresses."""
        return await self._call("public_request", "get_tokens", [])

    async def get_price(self, sell_token: str, buy_token: str, sell_amount: str) -> Any:  # noqa: ANN401
        """Get indicative prices. Amount is in sell-token atomic units."""
        return await self._call(
            "public_request",
            "get_price",
            _params(sellToken=sell_token, buyToken=buy_token, sellAmount=sell_amount),
        )

    async def get_quote(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: str,
        taker: str,
        *,
        slippage_bps: int | None = None,
        allow_wrapped: bool | None = None,
    ) -> Any:  # noqa: ANN401
        """Get firm quotes for wallet signing; this does not place a trade."""
        return await self._call(
            "public_request",
            "get_quote",
            _params(
                sellToken=sell_token,
                buyToken=buy_token,
                sellAmount=sell_amount,
                taker=taker,
                slippageBps=slippage_bps,
                allowWrapped=allow_wrapped,
            ),
        )

    async def get_status(self, tx_hash: str) -> Any:  # noqa: ANN401
        """Get normalized execution status for a submitted Arcus spot trade."""
        return await self._call("public_request", "get_status", _params(venue="arcus", id=tx_hash))

    async def build_signed_quote(
        self,
        quote: Mapping[str, Any],
        taker: str,
        signature: str,
        *,
        permits: list[Mapping[str, Any]] | None = None,
        route_tag: str | None = None,
    ) -> dict[str, Any]:
        """Build a validated submit body from an externally signed firm quote."""
        if self._native_client is None:
            await self.async_init()
        return self._native_client.build_signed_quote_json(
            json.dumps(dict(quote), separators=(",", ":")),
            taker,
            signature,
            None if permits is None else json.dumps(permits, separators=(",", ":")),
            route_tag,
        )

    async def submit_signed_quote(self, signed_quote: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a wallet-signed Arcus quote; this can execute a real spot trade."""
        return await self._call(
            "private_request",
            "submit_signed_quote",
            [("signed_quote_json", json.dumps(dict(signed_quote), separators=(",", ":")))],
        )

    async def close(self) -> None:
        """Release the native router client."""
        self._native_client = None
