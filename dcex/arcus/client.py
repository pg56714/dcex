# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Synchronous Arcus perpetuals REST client."""

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .._native_http import load_native, request_native_json
from ..base.http_manager import BaseHTTPManager
from ..utils.common import Common
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp


def _params(**kwargs: object) -> list[tuple[str, str]]:
    return [
        (name, str(value).lower() if isinstance(value, bool) else str(value))
        for name, value in kwargs.items()
        if value is not None
    ]


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

    def __post_init__(self) -> None:
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

    def _call(self, kind: str, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        try:
            response, data = request_native_json(self._native_client, kind, method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"Arcus {method_name}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    def public_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named read-only Arcus endpoint."""
        return self._call("public_request", method_name, _params(**params))

    def private_request(self, method_name: str, **params: object) -> Any:  # noqa: ANN401
        """Call a named signed Arcus order endpoint."""
        return self._call("private_request", method_name, _params(**params))

    def sign_websocket_request(
        self, request_id: int, method_name: str, **params: object
    ) -> dict[str, Any]:
        """
        Build a signed WS frame using the named REST method and its parameters.

        Does not submit an order. May fetch public market metadata for tick/step
        conversion. Batch fields (orders, cancels, modifies) accept lists.
        """
        encoded = {
            k: json.dumps(v, allow_nan=False) if isinstance(v, (list, dict)) else v
            for k, v in params.items()
        }
        result = json.loads(
            self._native_client.sign_websocket_request(request_id, method_name, _params(**encoded))
        )
        if not isinstance(result, dict):
            raise TypeError("Unexpected Arcus signed WebSocket frame")
        return result

    def get_markets(self) -> Any:  # noqa: ANN401
        """Get all perpetual markets."""
        return self.public_request("get_markets")

    def get_spot_assets(self) -> Any:  # noqa: ANN401
        """Get lending collateral assets; these are not RFQ spot pairs."""
        return self.public_request("get_spot_assets")

    def get_fee_tiers(self) -> Any:  # noqa: ANN401
        """Get exchange-wide perpetual fee tiers."""
        return self.public_request("get_fee_tiers")

    def get_account(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get a wallet account snapshot."""
        return self.public_request(
            "get_account", address=address or self.address, accountIndex=self.account_index
        )

    def get_bbo(self, market: str) -> Any:  # noqa: ANN401
        """Get the best bid and offer for a market such as BTC-USD."""
        return self.public_request("get_bbo", market=market)

    def get_l2_orderbook(self, market: str, depth: int | None = None) -> Any:  # noqa: ANN401
        """Get an L2 orderbook snapshot."""
        return self.public_request("get_l2_orderbook", market=market, nLevels=depth)

    def get_positions(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open positions for an address."""
        return self.public_request(
            "get_positions", address=address or self.address, accountIndex=self.account_index
        )

    def get_open_orders(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open orders for an address."""
        return self.public_request(
            "get_open_orders", address=address or self.address, accountIndex=self.account_index
        )

    def get_order_status(self, order_id: str, address: str | None = None) -> Any:  # noqa: ANN401
        """Get the current status of one order."""
        return self.public_request(
            "get_order_status",
            order_id=order_id,
            address=address or self.address,
            accountIndex=self.account_index,
        )

    def get_fills(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get account fills."""
        return self.public_request(
            "get_fills", address=address or self.address, accountIndex=self.account_index
        )

    def get_transfer_updates(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get deposits and internal-transfer updates for an address."""
        return self.public_request(
            "get_transfer_updates", address=address or self.address, accountIndex=self.account_index
        )

    def get_leverages(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get effective leverage and margin mode across markets."""
        return self.public_request(
            "get_leverages", address=address or self.address, accountIndex=self.account_index
        )

    def cancel_all_orders(
        self, product_symbol: str | None = None, valid_until: int | None = None
    ) -> Any:  # noqa: ANN401
        """Request cancel-all for this account, optionally limited to a market."""
        return self.private_request(
            "cancel_all_orders", product_symbol=product_symbol, valid_until=valid_until
        )

    def schedule_cancel(self, time: int, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Arm or refresh a cancel-all deadline (absolute epoch microseconds)."""
        return self.private_request("schedule_cancel", time=time, product_symbol=product_symbol)

    def disarm_scheduled_cancel(self, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Disarm the account-wide or market-scoped cancel-all deadline."""
        return self.private_request("disarm_scheduled_cancel", product_symbol=product_symbol)

    def adjust_isolated_margin(self, product_symbol: str, amount: str) -> Any:  # noqa: ANN401
        """Move signed dollar amount between cross collateral and an isolated leg."""
        return self.private_request(
            "adjust_isolated_margin", product_symbol=product_symbol, amount=amount
        )

    def set_leverage(
        self, product_symbol: str, leverage: int, *, isolated: bool | None = None
    ) -> Any:  # noqa: ANN401
        """Request a leverage or margin-mode change for one market."""
        return self.private_request(
            "set_leverage", product_symbol=product_symbol, leverage=leverage, isolated=isolated
        )

    def submit_internal_transfer(self, signed_transfer: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a same-wallet EIP-712-signed collateral transfer, not a withdrawal."""
        return self.private_request(
            "submit_internal_transfer",
            signed_transfer_json=json.dumps(dict(signed_transfer), separators=(",", ":")),
        )

    def place_order(
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
        return self.private_request(
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

    def modify_order(
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
        return self.private_request(
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

    def cancel_order(self, product_symbol: str, order_id: str) -> Any:  # noqa: ANN401
        """Submit an order cancellation."""
        return self.private_request(
            "cancel_order", product_symbol=product_symbol, order_id=order_id
        )

    def batch_place_orders(
        self, orders: list[dict[str, Any]], *, grouping: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Place orders, optionally grouped as partialTpsl, positionTpsl, or entryTpsl.

        TPSL legs use tpsl_type, stop_price, and reduce_only=True.
        positionTpsl legs require quantity="0"; entryTpsl starts with the entry.
        """
        return self.private_request(
            "batch_place_orders",
            orders=json.dumps(orders, separators=(",", ":")),
            grouping=grouping,
        )

    def batch_cancel_orders(self, cancels: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Cancel up to 100 individually signed orders in one request."""
        return self.private_request(
            "batch_cancel_orders", cancels=json.dumps(cancels, separators=(",", ":"))
        )

    def batch_modify_orders(self, modifies: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Modify up to 100 individually signed orders in one request."""
        return self.private_request(
            "batch_modify_orders", modifies=json.dumps(modifies, separators=(",", ":"))
        )

    def close(self) -> None:
        """Release the native client."""
        self._native_client = None

    def get_trade(self, *, trade_id: str, market: str) -> Any:  # noqa: ANN401
        """
        GET /v1/trade/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-a-single-trade-by-id.md
        """
        return self.public_request("get_trade", **{"trade_id": trade_id, "market": market})

    def get_account_stats(
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
        return self.public_request(
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

    def get_mid_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/mids; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-all-mid-prices.md
        """
        return self.public_request("get_mid_prices", **{"market": market})

    def get_compliance(self, *, address: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/compliance; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-compliance-status.md
        """
        return self.public_request("get_compliance", **{"address": address or self.address})

    def get_rate_limit(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/rateLimit; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-rate-limit-usage.md
        """
        return self.public_request(
            "get_rate_limit",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_time(self) -> Any:  # noqa: ANN401
        """
        GET /v1/time; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-server-time.md
        """
        return self.public_request("get_time", **{})

    def get_fill(
        self, *, trade_id: str, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/fill/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-fill-by-id.md
        """
        return self.public_request(
            "get_fill",
            **{
                "trade_id": trade_id,
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_funding(
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
        return self.public_request(
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

    def get_interest(
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
        return self.public_request(
            "get_interest",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "from": start_time,
                "to": end_time,
                "limit": limit,
            },
        )

    def get_live_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/prices; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-live-prices-for-all-markets.md
        """
        return self.public_request("get_live_prices", **{"market": market})

    def get_funding_rates(
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
        return self.public_request(
            "get_funding_rates",
            **{"market": market, "from": start_time, "to": end_time, "limit": limit},
        )

    def get_candles(
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
        return self.public_request(
            "get_candles",
            **{
                "market": market,
                "timeframe": timeframe,
                "to": end_time,
                "from": start_time,
                "countback": countback,
            },
        )

    def get_order_history(
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
        return self.public_request(
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

    def get_portfolio_history(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/portfolio; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-portfolio-history.md
        """
        return self.public_request(
            "get_portfolio_history",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_trades(
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
        return self.public_request(
            "get_trades", **{"market": market, "limit": limit, "from": start_time, "to": end_time}
        )

    def get_spot_fills(
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
        return self.public_request(
            "get_spot_fills",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "limit": limit,
                "from": start_time,
                "to": end_time,
            },
        )

    def get_spot_positions(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/spotPositions; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-spot-positions.md
        """
        return self.public_request(
            "get_spot_positions",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def health(self) -> Any:  # noqa: ANN401
        """
        GET /health; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/health-check.md
        """
        return self.public_request("health", **{})

    def get_service_info(self) -> Any:  # noqa: ANN401
        """
        GET /; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/service-info.md
        """
        return self.public_request("get_service_info", **{})

    def get_api_keys(self, *, address: str | None = None, account_index: int | None = None) -> Any:  # noqa: ANN401
        """List API keys; omitting account_index lists every subaccount scope."""
        return self.public_request(
            "get_api_keys", address=address or self.address, accountIndex=account_index
        )

    def create_api_key_signed(self, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Submit a caller wallet-authorized API key creation body unchanged.

        Sign the EIP-712 payload specified by the Arcus onboarding documentation.
        The trading API key cannot authorize this wallet operation.
        """
        return self.private_request(
            "create_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )

    def revoke_api_key_signed(self, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """Revoke an API key with a caller wallet-authorized signed body."""
        return self.private_request(
            "revoke_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )

    def get_market_metadata(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """Public market metadata."""
        return self.public_request("get_market_metadata", market=market)

    def get_market_overview(self) -> Any:  # noqa: ANN401
        """Public consolidated market overview."""
        return self.public_request("get_market_overview")

    def get_spot_market_overview(self) -> Any:  # noqa: ANN401
        """Public spot universe and reference data."""
        return self.public_request("get_spot_market_overview")

    def get_metadata_candles(
        self,
        *,
        market: str,
        timeframe: str,
        to: int,
        from_: int | None = None,
        countback: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Metadata candles: timestamps use seconds; from_ or countback is required."""
        return self.public_request(
            "get_metadata_candles",
            **{
                "market": market,
                "timeframe": timeframe,
                "to": to,
                "from": from_,
                "countback": countback,
            },
        )

    def get_user_preferences(self, *, address: str | None = None) -> Any:  # noqa: ANN401
        """Public preferences for the selected wallet."""
        return self.public_request("get_user_preferences", address=address or self.address)

    def upsert_user_preferences(self, preferences: dict[str, Any]) -> Any:  # noqa: ANN401
        """Patch preferences with the native Ed25519 signing key; no address in the body."""
        return self.private_request(
            "upsert_user_preferences",
            preferences=json.dumps(preferences, separators=(",", ":"), allow_nan=False),
        )

    def delete_user_preference_signed(self, *, key: str, timestamp: int, signature: str) -> Any:  # noqa: ANN401
        """Delete a preference using caller signing headers; timestamp is nanoseconds."""
        return self.private_request(
            "delete_user_preference_signed", key=key, timestamp=timestamp, signature=signature
        )

    def get_leaderboard(
        self,
        *,
        window: str | None = None,
        sort_by: str | None = None,
        address: str | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Query trader rankings; PnL is realized and the hourly rollup can lag."""
        return self.public_request(
            "get_leaderboard",
            **{
                k: v
                for k, v in {
                    "window": window,
                    "sortBy": sort_by,
                    "address": address,
                    "limit": limit,
                }.items()
                if v is not None
            },
        )

    def create_withdrawal_signed(
        self,
        *,
        ethereum_address: str,
        amount: str,
        nonce: str,
        signature: dict[str, str],
        account_index: int | None = None,
        spot_asset_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/withdraw.

        API withdrawals have no second confirmation; they execute on submit. Amount is an integer
        quantum string. Supply a wallet EIP-712 signature; no API key headers are sent.
        Source: https://docs.arcus.xyz/api-reference/exchange/submit-withdrawal
        """
        return self.private_request(
            "create_withdrawal_signed",
            **{
                "ethereumAddress": ethereum_address,
                "accountIndex": account_index,
                "spotAssetId": spot_asset_id,
                "amount": amount,
                "nonce": nonce,
                "signature": json.dumps(signature, separators=(",", ":"), allow_nan=False),
            },
        )

    def create_withdrawal(
        self, *, ethereum_address: str, amount: str, nonce: str, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/withdraw.

        API withdrawals have no second confirmation; they execute on submit. Amount is an integer
        quantum string. USDG only; the API key must carry operator-provisioned withdraw permission.
        Source: https://docs.arcus.xyz/api-reference/exchange/submit-withdrawal
        """
        return self.private_request(
            "create_withdrawal",
            **{
                "ethereumAddress": ethereum_address,
                "accountIndex": account_index,
                "amount": amount,
                "nonce": nonce,
            },
        )

    def get_commission_rates(self) -> Any:  # noqa: ANN401
        """
        GET /v1/commissionrates.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/public/get-referral-commission-rate-schedule
        """
        return self.public_request("get_commission_rates", **{})

    def check_referral_code(self, *, code: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/codeAvailable.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/check-whether-a-referral-code-is-available
        """
        return self.public_request("check_referral_code", **{"code": code})

    def claim_affiliate_commission(
        self, *, address: str, cutoff_fill_id: int | None = None, amount_quantums: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/claim.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/claim-accrued-commission
        """
        return self.private_request(
            "claim_affiliate_commission",
            **{
                "address": address,
                "cutoffFillId": cutoff_fill_id,
                "amountQuantums": amount_quantums,
            },
        )

    def create_referral_code(self, *, address: str, code: str, kickback_bps: int) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/createCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/create-referral-code
        """
        return self.private_request(
            "create_referral_code",
            **{"address": address, "code": code, "kickbackBps": kickback_bps},
        )

    def get_affiliate_claims(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/claims.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-claim-history
        """
        return self.public_request(
            "get_affiliate_claims", **{"address": address, "from": from_, "to": to, "limit": limit}
        )

    def get_affiliate_commissions(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/commissions.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-commission-history
        """
        return self.private_request(
            "get_affiliate_commissions",
            **{"address": address, "from": from_, "to": to, "limit": limit, "cursor": cursor},
        )

    def get_affiliate_info(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/info.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-info
        """
        return self.private_request("get_affiliate_info", **{"address": address})

    def get_affiliate_leaderboard(self, *, limit: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/leaderboard.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-leaderboard
        """
        return self.public_request("get_affiliate_leaderboard", **{"limit": limit})

    def get_referrer(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/myReferrer.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-my-referrer
        """
        return self.public_request("get_referrer", **{"address": address})

    def get_referees(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/referees.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-referees
        """
        return self.private_request(
            "get_referees",
            **{"address": address, "from": from_, "to": to, "limit": limit, "cursor": cursor},
        )

    def get_referral_code(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/code.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-the-callers-referral-code
        """
        return self.private_request("get_referral_code", **{"address": address})

    def get_invite_codes(
        self,
        *,
        address: str,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/inviteCodes.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/list-the-callers-invite-codes
        """
        return self.private_request(
            "get_invite_codes",
            **{"address": address, "status": status, "limit": limit, "offset": offset},
        )

    def get_affiliate_claim(self, *, address: str, id: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/claimStatus.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/look-up-a-single-claim
        """
        return self.public_request("get_affiliate_claim", **{"address": address, "id": id})

    def redeem_invite_code(self, *, address: str, invite_code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/redeemInvite.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/redeem-an-invite-code
        """
        return self.private_request(
            "redeem_invite_code", **{"address": address, "inviteCode": invite_code}
        )

    def register_referral(self, *, address: str, code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/registerAffiliate.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/register-as-referee
        """
        return self.private_request("register_referral", **{"address": address, "code": code})

    def rename_referral_code(self, *, address: str, code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/modifyCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/rename-referral-code
        """
        return self.private_request("rename_referral_code", **{"address": address, "code": code})

    def revoke_referral_code(self, *, address: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/revokeCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/revoke-referral-code
        """
        return self.private_request("revoke_referral_code", **{"address": address})

    def update_referral_kickback(self, *, address: str, kickback_bps: int) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/kickback.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/update-kickback-rate
        """
        return self.private_request(
            "update_referral_kickback", **{"address": address, "kickbackBps": kickback_bps}
        )
