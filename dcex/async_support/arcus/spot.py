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
    wallet_address: str | None = None
    rpc_url: str | None = None
    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    async def async_init(self) -> Self:
        """Initialize the native spot router client."""
        self.wallet_address = self.wallet_address or os.getenv("ARCUS_ADDRESS")
        self._native_client = load_native().ArcusSpotHttpClient(
            api_key=self.api_key,
            testnet=self.testnet,
            timeout=self.timeout,
            base_url=self.base_url,
            wallet_address=self.wallet_address,
            rpc_url=self.rpc_url,
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

    async def get_price(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: str,
        *,
        builder_fee_bps: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get indicative prices. Amount is in sell-token atomic units."""
        return await self._call(
            "public_request",
            "get_price",
            _params(
                sellToken=sell_token,
                buyToken=buy_token,
                sellAmount=sell_amount,
                builderFeeBps=builder_fee_bps,
            ),
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
        builder_fee_bps: int | None = None,
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
                builderFeeBps=builder_fee_bps,
            ),
        )

    async def get_native_balance(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Read the Robinhood Chain ETH balance in wei, without a Perps API key."""
        return await self._call("public_request", "get_native_balance", _params(address=address))

    async def get_token_balance(self, token: str, address: str | None = None) -> Any:  # noqa: ANN401
        """Read an ERC-20 balance in atomic units."""
        return await self._call(
            "public_request", "get_token_balance", _params(token=token, address=address)
        )

    async def get_balances(
        self,
        address: str | None = None,
        *,
        tokens: list[str | dict[str, Any]] | None = None,
        include_wrapped: bool = True,
    ) -> Any:  # noqa: ANN401
        """Read ETH, listed tokens, and their wrapped representations by default."""
        return await self._call(
            "public_request",
            "get_balances",
            _params(
                address=address,
                tokens_json=None if tokens is None else json.dumps(tokens),
                include_wrapped=None if include_wrapped else False,
            ),
        )

    async def get_allowance(
        self, token: str, address: str | None = None, *, spender: str | None = None
    ) -> Any:  # noqa: ANN401
        """Read token allowance; the default spender is canonical Permit2."""
        return await self._call(
            "public_request",
            "get_allowance",
            _params(token=token, address=address, spender=spender),
        )

    async def get_block_number(self) -> Any:  # noqa: ANN401
        """Read the current Robinhood Chain block number for history paging."""
        return await self._call("public_request", "get_block_number", [])

    async def get_transaction_receipt(self, tx_hash: str) -> Any:  # noqa: ANN401
        """Read a transaction receipt; returns None while still pending."""
        return await self._call(
            "public_request", "get_transaction_receipt", _params(tx_hash=tx_hash)
        )

    async def get_trade_history(
        self,
        from_block: int,
        to_block: int | None = None,
        *,
        address: str | None = None,
        token_in: str | None = None,
        token_out: str | None = None,
        swap_shell: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Read SwapShell fills for a bounded block range; page large histories."""
        return await self._call(
            "public_request",
            "get_trade_history",
            _params(
                from_block=from_block,
                to_block=to_block,
                address=address,
                token_in=token_in,
                token_out=token_out,
                swap_shell=swap_shell,
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
        builder_fee_bps: int | None = None,
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
            builder_fee_bps,
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
