"""Asynchronous Arcus perpetuals REST client."""

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
class Client(BaseHTTPManager):
    """Arcus perps; pass testnet=True for the independent testnet credentials."""

    EXCHANGE = Common.ARCUS
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    address: str | None = None
    account_index: int | None = None
    testnet: bool = False
    timeout: float = 10.0
    base_url: str | None = None
    _native_client: Any = field(default=None, init=False, repr=False)  # noqa: ANN401

    async def async_init(self) -> Self:
        """Initialize the native client with the selected network credentials."""
        prefix = "ARCUS_TESTNET" if self.testnet else "ARCUS_MAINNET"
        self.api_key = self.api_key or os.getenv(f"{prefix}_API_KEY") or None
        self.api_secret = self.api_secret or os.getenv(f"{prefix}_API_SIGNING_KEY") or None
        self.address = self.address or os.getenv(f"{prefix}_ADDRESS") or None
        if self.account_index is None:
            self.account_index = int(os.getenv(f"{prefix}_ACCOUNT_INDEX", "0"))
        self._native_client = load_native().ArcusHttpClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            address=self.address,
            account_index=self.account_index,
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
                request=f"Arcus {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    async def public_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named read-only Arcus endpoint."""
        return await self._call("public_request", method_name, _params(**params))

    async def private_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named signed Arcus order endpoint."""
        return await self._call("private_request", method_name, _params(**params))

    async def get_markets(self) -> Any:  # noqa: ANN401
        """Get all perpetual markets."""
        return await self.public_request("get_markets")

    async def get_spot_assets(self) -> Any:  # noqa: ANN401
        """Get lending collateral assets; these are not RFQ spot pairs."""
        return await self.public_request("get_spot_assets")

    async def get_fee_tiers(self) -> Any:  # noqa: ANN401
        """Get exchange-wide perpetual fee tiers."""
        return await self.public_request("get_fee_tiers")

    async def get_account(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get a wallet account snapshot."""
        return await self.public_request(
            "get_account", address=address or self.address, accountIndex=self.account_index
        )

    async def get_bbo(self, market: str) -> Any:  # noqa: ANN401
        """Get the best bid and offer for a market such as BTC-USD."""
        return await self.public_request("get_bbo", market=market)

    async def get_l2_orderbook(self, market: str, depth: int | None = None) -> Any:  # noqa: ANN401
        """Get an L2 orderbook snapshot."""
        return await self.public_request("get_l2_orderbook", market=market, nLevels=depth)

    async def get_positions(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open positions for an address."""
        return await self.public_request(
            "get_positions", address=address or self.address, accountIndex=self.account_index
        )

    async def get_open_orders(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open orders for an address."""
        return await self.public_request(
            "get_open_orders", address=address or self.address, accountIndex=self.account_index
        )

    async def get_order_status(self, order_id: str, address: str | None = None) -> Any:  # noqa: ANN401
        """Get the current status of one order."""
        return await self.public_request(
            "get_order_status",
            order_id=order_id,
            address=address or self.address,
            accountIndex=self.account_index,
        )

    async def get_fills(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get account fills."""
        return await self.public_request(
            "get_fills", address=address or self.address, accountIndex=self.account_index
        )

    async def get_transfer_updates(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get deposits and internal-transfer updates for an address."""
        return await self.public_request(
            "get_transfer_updates", address=address or self.address, accountIndex=self.account_index
        )

    async def get_leverages(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get effective leverage and margin mode across markets."""
        return await self.public_request(
            "get_leverages", address=address or self.address, accountIndex=self.account_index
        )

    async def cancel_all_orders(
        self, product_symbol: str | None = None, valid_until: int | None = None
    ) -> Any:  # noqa: ANN401
        """Request cancel-all for this account, optionally limited to a market."""
        return await self.private_request(
            "cancel_all_orders", product_symbol=product_symbol, valid_until=valid_until
        )

    async def set_leverage(
        self, product_symbol: str, leverage: int, *, isolated: bool | None = None
    ) -> Any:  # noqa: ANN401
        """Request a leverage or margin-mode change for one market."""
        return await self.private_request(
            "set_leverage", product_symbol=product_symbol, leverage=leverage, isolated=isolated
        )

    async def submit_internal_transfer(self, signed_transfer: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a same-wallet EIP-712-signed collateral transfer, not a withdrawal."""
        return await self.private_request(
            "submit_internal_transfer",
            signed_transfer_json=json.dumps(dict(signed_transfer), separators=(",", ":")),
        )

    async def place_order(
        self,
        product_symbol: str,
        side: str,
        price: str,
        quantity: str,
        *,
        order_type: str = "LIMIT",
        time_in_force: str = "GTT",
        good_til_time: int | None = None,
        reduce_only: bool = False,
        client_order_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Submit an order; REST 200/202 is acknowledgement, not a confirmed fill."""
        return await self.private_request(
            "place_order",
            product_symbol=product_symbol,
            side=side,
            price=price,
            quantity=quantity,
            order_type=order_type,
            time_in_force=time_in_force,
            good_til_time=good_til_time,
            reduce_only=reduce_only,
            client_order_id=client_order_id,
        )

    async def modify_order(
        self,
        product_symbol: str,
        side: str,
        price: str,
        quantity: str,
        good_til_time: int,
        time_in_force: str,
        reduce_only: bool,
        *,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Modify one Perps order by server or client ID; acknowledgement is not a fill."""
        return await self.private_request(
            "modify_order",
            product_symbol=product_symbol,
            side=side,
            price=price,
            quantity=quantity,
            good_til_time=good_til_time,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            order_id=order_id,
            client_order_id=client_order_id,
        )

    async def cancel_order(self, product_symbol: str, order_id: str) -> Any:  # noqa: ANN401
        """Submit an order cancellation."""
        return await self.private_request(
            "cancel_order", product_symbol=product_symbol, order_id=order_id
        )

    async def close(self) -> None:
        """Release the native client."""
        self._native_client = None
