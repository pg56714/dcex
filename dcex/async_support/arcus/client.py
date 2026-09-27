# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Asynchronous Arcus perpetuals REST client."""

import json
import os
from collections.abc import Mapping, Sequence
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
    """Arcus perps; pass testnet=True to select the testnet endpoint."""

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
        """Initialize the native client for the selected network."""
        self.api_key = self.api_key or os.getenv("ARCUS_API_KEY") or None
        self.api_secret = self.api_secret or os.getenv("ARCUS_API_SIGNING_KEY") or None
        self.address = self.address or os.getenv("ARCUS_ADDRESS") or None
        if self.account_index is None:
            self.account_index = 0
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

    async def sign_websocket_request(
        self, request_id: int, method_name: str, **params: object
    ) -> dict[str, Any]:
        """
        Build a signed WS frame using the named REST method and its parameters.

        Does not submit an order. May fetch public market metadata for tick/step
        conversion. Batch fields (orders, cancels, modifies) accept lists.
        """
        if self._native_client is None:
            await self.async_init()
        encoded = {
            k: json.dumps(v, allow_nan=False) if isinstance(v, (list, dict)) else v
            for k, v in params.items()
        }
        result = json.loads(
            await self._native_client.sign_websocket_request_async(
                request_id, method_name, _params(**encoded)
            )
        )
        if not isinstance(result, dict):
            raise TypeError("Unexpected Arcus signed WebSocket frame")
        return result

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

    async def schedule_cancel(self, time: int, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Arm or refresh a cancel-all deadline (absolute epoch microseconds)."""
        return await self.private_request(
            "schedule_cancel", time=time, product_symbol=product_symbol
        )

    async def disarm_scheduled_cancel(self, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Disarm the account-wide or market-scoped cancel-all deadline."""
        return await self.private_request("disarm_scheduled_cancel", product_symbol=product_symbol)

    async def adjust_isolated_margin(self, product_symbol: str, amount: str) -> Any:  # noqa: ANN401
        """Move signed dollar amount between cross collateral and an isolated leg."""
        return await self.private_request(
            "adjust_isolated_margin", product_symbol=product_symbol, amount=amount
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

    async def batch_place_orders(
        self, orders: list[dict[str, Any]], *, grouping: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Place orders, optionally grouped as partialTpsl, positionTpsl, or entryTpsl.

        TPSL legs use tpsl_type, stop_price, and reduce_only=True.
        positionTpsl legs require quantity="0"; entryTpsl starts with the entry.
        """
        return await self.private_request(
            "batch_place_orders",
            orders=json.dumps(orders, separators=(",", ":")),
            grouping=grouping,
        )

    async def batch_cancel_orders(self, cancels: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Cancel up to 100 individually signed orders in one request."""
        return await self.private_request(
            "batch_cancel_orders", cancels=json.dumps(cancels, separators=(",", ":"))
        )

    async def batch_modify_orders(self, modifies: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Modify up to 100 individually signed orders in one request."""
        return await self.private_request(
            "batch_modify_orders", modifies=json.dumps(modifies, separators=(",", ":"))
        )

    async def close(self) -> None:
        """Release the native client."""
        self._native_client = None

    async def get_trade(self, *, trade_id: str, market: str) -> Any:  # noqa: ANN401
        """
        GET /v1/trade/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-a-single-trade-by-id.md
        """
        return await self.public_request("get_trade", **{"trade_id": trade_id, "market": market})

    async def get_account_stats(
        self,
        *,
        address: str | None = None,
        include: str | Sequence[str] | None = None,
        windows: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/account/stats; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-account-stats.md
        """
        return await self.public_request(
            "get_account_stats",
            **{
                "address": address or self.address,
                "include": include
                if isinstance(include, str) or include is None
                else ",".join(include),
                "windows": windows
                if isinstance(windows, str) or windows is None
                else ",".join(windows),
            },
        )

    async def get_mid_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/mids; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-all-mid-prices.md
        """
        return await self.public_request("get_mid_prices", **{"market": market})

    async def get_compliance(self, *, address: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/compliance; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-compliance-status.md
        """
        return await self.public_request("get_compliance", **{"address": address or self.address})

    async def get_rate_limit(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/rateLimit; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-rate-limit-usage.md
        """
        return await self.public_request(
            "get_rate_limit",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    async def get_time(self) -> Any:  # noqa: ANN401
        """
        GET /v1/time; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-server-time.md
        """
        return await self.public_request("get_time", **{})

    async def get_fill(
        self, *, trade_id: str, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/fill/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-fill-by-id.md
        """
        return await self.public_request(
            "get_fill",
            **{
                "trade_id": trade_id,
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    async def get_funding(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        market: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/funding; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-funding-payments.md
        """
        return await self.public_request(
            "get_funding",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "market": market,
                "from": start_time,
                "to": end_time,
                "limit": limit,
            },
        )

    async def get_interest(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/interest; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-interest-payments.md
        """
        return await self.public_request(
            "get_interest",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "from": start_time,
                "to": end_time,
                "limit": limit,
            },
        )

    async def get_live_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/prices; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-live-prices-for-all-markets.md
        """
        return await self.public_request("get_live_prices", **{"market": market})

    async def get_funding_rates(
        self,
        *,
        market: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/fundingRates; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-market-funding-rates.md
        """
        return await self.public_request(
            "get_funding_rates",
            **{"market": market, "from": start_time, "to": end_time, "limit": limit},
        )

    async def get_candles(
        self,
        *,
        market: str,
        timeframe: str,
        end_time: int,
        start_time: int | None = None,
        countback: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/candles; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-ohlcv-candles.md
        """
        return await self.public_request(
            "get_candles",
            **{
                "market": market,
                "timeframe": timeframe,
                "to": end_time,
                "from": start_time,
                "countback": countback,
            },
        )

    async def get_order_history(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        market: str | None = None,
        side: str | None = None,
        status: str | Sequence[str] | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/orders; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-order-history.md
        """
        return await self.public_request(
            "get_order_history",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "market": market,
                "side": side,
                "status": status if isinstance(status, str) or status is None else ",".join(status),
                "limit": limit,
                "from": start_time,
                "to": end_time,
            },
        )

    async def get_portfolio_history(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/portfolio; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-portfolio-history.md
        """
        return await self.public_request(
            "get_portfolio_history",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    async def get_trades(
        self,
        *,
        market: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/trades; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-recent-public-trades.md
        """
        return await self.public_request(
            "get_trades", **{"market": market, "limit": limit, "from": start_time, "to": end_time}
        )

    async def get_spot_fills(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/spotFills; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-spot-fills.md
        """
        return await self.public_request(
            "get_spot_fills",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "limit": limit,
                "from": start_time,
                "to": end_time,
            },
        )

    async def get_spot_positions(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/spotPositions; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-spot-positions.md
        """
        return await self.public_request(
            "get_spot_positions",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    async def health(self) -> Any:  # noqa: ANN401
        """
        GET /health; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/health-check.md
        """
        return await self.public_request("health", **{})

    async def get_service_info(self) -> Any:  # noqa: ANN401
        """
        GET /; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/service-info.md
        """
        return await self.public_request("get_service_info", **{})

    async def get_api_keys(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:
        """List API keys; omitting account_index lists every subaccount scope."""
        return await self.public_request(
            "get_api_keys", address=address or self.address, accountIndex=account_index
        )

    async def create_api_key_signed(self, body: dict[str, Any]) -> Any:
        """
        Submit a caller wallet-authorized API key creation body unchanged.

        Sign the EIP-712 payload specified by the Arcus onboarding documentation.
        The trading API key cannot authorize this wallet operation.
        """
        return await self.private_request(
            "create_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )

    async def revoke_api_key_signed(self, body: dict[str, Any]) -> Any:
        """Revoke an API key with a caller wallet-authorized signed body."""
        return await self.private_request(
            "revoke_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )
