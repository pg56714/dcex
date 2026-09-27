"""Extended async account HTTP client backed by Rust."""

from collections.abc import Mapping, Sequence
from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for Extended account endpoints."""

    async def get_account_details(self) -> Any:  # noqa: ANN401
        return await self._native_private("get_account_details", [])

    async def get_sub_accounts(self) -> Any:  # noqa: ANN401
        return await self._native_private("get_sub_accounts", [])

    async def get_balance(self) -> Any:  # noqa: ANN401
        return await self._native_private("get_balance", [])

    async def get_asset_operations(
        self,
        accountId: int | Sequence[int] | None = None,  # noqa: N803
        id: int | str | None = None,  # noqa: A002
        type: str | Sequence[str] | None = None,  # noqa: A002
        status: str | Sequence[str] | None = None,
        startTime: int | None = None,  # noqa: N803
        endTime: int | None = None,  # noqa: N803
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get deposit, withdrawal, and transfer history."""
        return await self._native_private(
            "get_asset_operations",
            self._native_params(
                accountId=accountId,
                id=id,
                type=type,
                status=status,
                startTime=startTime,
                endTime=endTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def submit_internal_transfer(self, body: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a pre-signed transfer between subaccounts of the same wallet."""
        return await self._native_private(
            "submit_internal_transfer", self._native_params(body=dict(body))
        )

    async def get_account_health(
        self,
        accountId: int | Sequence[int],  # noqa: N803
    ) -> Any:  # noqa: ANN401
        """Get live health and margin metrics for one or more subaccounts."""
        return await self._native_private(
            "get_account_health", self._native_params(accountId=accountId)
        )

    async def get_spot_balances(
        self,
        accountId: int | Sequence[int] | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_spot_balances",
            self._native_params(accountId=accountId),
        )

    async def get_positions(
        self,
        market: str | Sequence[str] | None = None,
        side: str | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_positions",
            self._native_params(market=market, side=side),
        )

    async def get_positions_history(
        self,
        market: str | Sequence[str] | None = None,
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_positions_history",
            self._native_params(market=market, side=side, cursor=cursor, limit=limit),
        )

    async def get_trades_history(
        self,
        market: str | Sequence[str] | None = None,
        type: str | None = None,  # noqa: A002
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_trades_history",
            self._native_params(
                market=market,
                type=type,
                side=side,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def get_funding_payments(
        self,
        startTime: int,  # noqa: N803
        market: str | Sequence[str] | None = None,
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_funding_payments",
            self._native_params(
                market=market,
                side=side,
                startTime=startTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def get_leverage(
        self,
        market: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private("get_leverage", self._native_params(market=market))

    async def update_leverage(self, market: str, leverage: str | int) -> Any:  # noqa: ANN401
        """Update the leverage for one market (``PATCH /api/v1/user/leverage``)."""
        return await self._native_private(
            "update_leverage",
            self._native_params(market=market, leverage=leverage),
        )

    async def get_fees(
        self,
        market: str | Sequence[str] | None = None,
        builderId: int | str | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_fees",
            self._native_params(market=market, builderId=builderId),
        )

    async def get_rebates(self) -> Any:  # noqa: ANN401
        """Get account rebate statistics."""
        return await self._native_private("get_rebates", [])

    async def get_builder_dashboard(self) -> Any:  # noqa: ANN401
        """Get statistics for the authenticated builder."""
        return await self._native_private("get_builder_dashboard", [])

    async def get_builder_trades(
        self,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get trade history for the authenticated builder."""
        return await self._native_private(
            "get_builder_trades",
            self._native_params(cursor=cursor, limit=limit),
        )

    async def get_bridge_config(self) -> Any:  # noqa: ANN401
        """Get chains supported by the Extended bridge."""
        return await self._native_private("get_bridge_config", [])

    async def get_bridge_quote(
        self,
        chainIn: str,  # noqa: N803
        chainOut: str,  # noqa: N803
        amount: str | int | float,
        asset: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Get a non-binding bridge quote."""
        return await self._native_private(
            "get_bridge_quote",
            self._native_params(
                chainIn=chainIn,
                chainOut=chainOut,
                amount=amount,
                asset=asset,
            ),
        )

    async def get_account_equity_history(
        self, *, account_id: int | Sequence[int], interval: str
    ) -> Any:  # noqa: ANN401
        """
        Get account equity history.

        Source: https://api.docs.extended.exchange/#get-account-equity-history
        """
        return await self._native_private(
            "get_account_equity_history",
            self._native_params(accountId=account_id, interval=interval),
        )

    async def get_account_pnl_history(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        pnl_type: str,
        instrument_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get account pnl history.

        Source: https://api.docs.extended.exchange/#get-account-pnl-history
        """
        return await self._native_private(
            "get_account_pnl_history",
            self._native_params(
                accountId=account_id,
                interval=interval,
                pnlType=pnl_type,
                instrumentType=instrument_type,
            ),
        )

    async def get_account_pnl_percentage_history(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        pnl_type: str,
        price_market: str | Sequence[str] | None = None,
        instrument_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get account pnl percentage history.

        Source: https://api.docs.extended.exchange/#get-account-pnl-percentage-history
        """
        return await self._native_private(
            "get_account_pnl_percentage_history",
            self._native_params(
                accountId=account_id,
                interval=interval,
                pnlType=pnl_type,
                priceMarket=price_market,
                instrumentType=instrument_type,
            ),
        )

    async def get_cumulative_account_pnl_history(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        pnl_type: str,
        instrument_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get cumulative account pnl history.

        Source: https://api.docs.extended.exchange/#get-cumulative-account-pnl-history
        """
        return await self._native_private(
            "get_cumulative_account_pnl_history",
            self._native_params(
                accountId=account_id,
                interval=interval,
                pnlType=pnl_type,
                instrumentType=instrument_type,
            ),
        )

    async def get_cumulative_account_pnl_percentage_history(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        pnl_type: str,
        price_market: str | Sequence[str] | None = None,
        instrument_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get cumulative account pnl percentage history.

        Source: https://api.docs.extended.exchange/#get-cumulative-account-pnl-percentage-history
        """
        return await self._native_private(
            "get_cumulative_account_pnl_percentage_history",
            self._native_params(
                accountId=account_id,
                interval=interval,
                pnlType=pnl_type,
                priceMarket=price_market,
                instrumentType=instrument_type,
            ),
        )

    async def get_account_vault_equity_history(
        self, *, account_id: int | Sequence[int], interval: str
    ) -> Any:  # noqa: ANN401
        """
        Get account vault equity history.

        Source: https://api.docs.extended.exchange/#get-account-vault-equity-history
        """
        return await self._native_private(
            "get_account_vault_equity_history",
            self._native_params(accountId=account_id, interval=interval),
        )

    async def get_account_max_drawdown_history(
        self, *, account_id: int | Sequence[int], interval: str
    ) -> Any:  # noqa: ANN401
        """
        Get account max drawdown history.

        Source: https://api.docs.extended.exchange/#get-account-max-drawdown-history
        """
        return await self._native_private(
            "get_account_max_drawdown_history",
            self._native_params(accountId=account_id, interval=interval),
        )

    async def get_account_funding_chart(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        market: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get account funding chart.

        Source: https://api.docs.extended.exchange/#get-account-funding-chart
        """
        return await self._native_private(
            "get_account_funding_chart",
            self._native_params(accountId=account_id, interval=interval, market=market),
        )

    async def get_account_portfolio_summary(
        self, *, account_id: int | Sequence[int], interval: str, instrument_type: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get account portfolio summary.

        Source: https://api.docs.extended.exchange/#get-account-portfolio-summary
        """
        return await self._native_private(
            "get_account_portfolio_summary",
            self._native_params(
                accountId=account_id, interval=interval, instrumentType=instrument_type
            ),
        )

    async def get_account_performance(
        self, *, account_id: int | Sequence[int], interval: str, market_type: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get account performance.

        Source: https://api.docs.extended.exchange/#get-account-performance
        """
        return await self._native_private(
            "get_account_performance",
            self._native_params(accountId=account_id, interval=interval, marketType=market_type),
        )

    async def get_account_funding_stats(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        market: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get account funding stats.

        Source: https://api.docs.extended.exchange/#get-account-funding-stats
        """
        return await self._native_private(
            "get_account_funding_stats",
            self._native_params(accountId=account_id, interval=interval, market=market),
        )

    async def get_account_funding_history(
        self,
        *,
        account_id: int | Sequence[int],
        interval: str,
        market: str | Sequence[str] | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get account funding history.

        Source: https://api.docs.extended.exchange/#get-account-funding-history
        """
        return await self._native_private(
            "get_account_funding_history",
            self._native_params(
                accountId=account_id, interval=interval, market=market, cursor=cursor, limit=limit
            ),
        )

    async def get_interest_key_metrics(self, *, account_id: int | Sequence[int]) -> Any:  # noqa: ANN401
        """
        Get interest key metrics.

        Source: https://api.docs.extended.exchange/#get-interest-key-metrics
        """
        return await self._native_private(
            "get_interest_key_metrics", self._native_params(accountId=account_id)
        )

    async def get_interest_daily_metrics(
        self, *, account_id: int | Sequence[int], interval: str
    ) -> Any:  # noqa: ANN401
        """
        Get interest daily metrics.

        Source: https://api.docs.extended.exchange/#get-interest-daily-metrics
        """
        return await self._native_private(
            "get_interest_daily_metrics",
            self._native_params(accountId=account_id, interval=interval),
        )

    async def get_interest_payment_chart(
        self, *, account_id: int | Sequence[int], interval: str, bucket: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get interest payment chart.

        Source: https://api.docs.extended.exchange/#get-interest-payment-chart
        """
        return await self._native_private(
            "get_interest_payment_chart",
            self._native_params(accountId=account_id, interval=interval, bucket=bucket),
        )

    async def get_interest_payments_history(
        self, *, account_id: int | Sequence[int], interval: str
    ) -> Any:  # noqa: ANN401
        """
        Get interest payments history.

        Source: https://api.docs.extended.exchange/#get-interest-payments-history
        """
        return await self._native_private(
            "get_interest_payments_history",
            self._native_params(accountId=account_id, interval=interval),
        )

    async def get_earned_points(self) -> Any:  # noqa: ANN401
        """GET /api/v1/user/rewards/earned."""
        return await self._native_private("get_earned_points", self._native_params())

    async def get_points_leaderboard_stats(self) -> Any:  # noqa: ANN401
        """GET /api/v1/user/rewards/leaderboard/stats."""
        return await self._native_private("get_points_leaderboard_stats", self._native_params())
