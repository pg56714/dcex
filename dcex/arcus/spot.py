"""
Synchronous Arcus spot RFQ router client.

Perpetual API credentials cannot sign spot trades. An EVM wallet must sign the
firm quote's EIP-712 typed data before submission.
"""

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .._native_http import load_native, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from .client import _params


@dataclass
class SpotClient(BaseHTTPManager):
    """Arcus spot RFQ router; independent of the perpetuals client."""

    EXCHANGE = Common.ARCUS
    api_key: str | None = field(default=None, repr=False)
    testnet: bool = False
    timeout: float = 10.0
    base_url: str | None = None
    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    def __post_init__(self) -> None:
        prefix = "ARCUS_SPOT_TESTNET" if self.testnet else "ARCUS_SPOT_MAINNET"
        self.api_key = self.api_key or os.getenv(f"{prefix}_API_KEY") or None
        self._native_client = load_native().ArcusSpotHttpClient(
            api_key=self.api_key,
            testnet=self.testnet,
            timeout=self.timeout,
            base_url=self.base_url,
        )

    def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        try:
            response, data = request_native_json(self._native_client, kind, method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Arcus Spot {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    def health(self) -> Any:  # noqa: ANN401
        """Get the router's unversioned health status."""
        return self._call("public_request", "health", [])

    def get_tokens(self) -> Any:  # noqa: ANN401
        """Get supported spot tokens and their on-chain addresses."""
        return self._call("public_request", "get_tokens", [])

    def get_price(self, sell_token: str, buy_token: str, sell_amount: str) -> Any:  # noqa: ANN401
        """Get indicative prices. Amount is in sell-token atomic units."""
        return self._call(
            "public_request",
            "get_price",
            _params(sellToken=sell_token, buyToken=buy_token, sellAmount=sell_amount),
        )

    def get_quote(
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
        return self._call(
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

    def get_status(self, tx_hash: str) -> Any:  # noqa: ANN401
        """Get normalized execution status for a submitted Arcus spot trade."""
        return self._call("public_request", "get_status", _params(venue="arcus", id=tx_hash))

    def submit_signed_quote(self, signed_quote: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a wallet-signed Arcus quote; this can execute a real spot trade."""
        return self._call(
            "private_request",
            "submit_signed_quote",
            [("signed_quote_json", json.dumps(dict(signed_quote), separators=(",", ":")))],
        )

    def close(self) -> None:
        """Release the native router client."""
        self._native_client = None
