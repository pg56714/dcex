"""Lighter async public market-data HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for Lighter public REST APIs."""

    async def get_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API service info."""
        return await self._native_public("get_info", self._native_params(**locals()))

    async def get_status(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API service status."""
        return await self._native_public("get_status", self._native_params(**locals()))

    async def get_announcement(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter announcements."""
        return await self._native_public("get_announcement", self._native_params(**locals()))

    async def get_order_book_details(
        self,
        market_id: int | None = None,
        filter: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order book metadata."""
        return await self._native_public("get_order_book_details", self._native_params(**locals()))

    async def get_order_books(
        self,
        market_id: int | None = None,
        filter: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order books."""
        return await self._native_public("get_order_books", self._native_params(**locals()))

    async def get_order_book_orders(
        self,
        market_id: int,
        limit: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order book orders."""
        return await self._native_public("get_order_book_orders", self._native_params(**locals()))

    async def get_recent_trades(
        self,
        market_id: int,
        limit: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Lighter trades."""
        return await self._native_public("get_recent_trades", self._native_params(**locals()))

    async def get_trades(
        self,
        sort_by: str,
        limit: int,
        market_id: int | None = None,
        market_type: str | None = None,
        account_index: int | None = None,
        order_index: int | None = None,
        sort_dir: str | None = None,
        cursor: str | None = None,
        from_: int | None = None,
        ask_filter: int | None = None,
        role: str | None = None,
        type_: str | None = None,
        aggregate: bool | None = None,
        skip_ask_order_id: str | None = None,
        skip_bid_order_id: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve auth-gated Lighter trades."""
        return await self._native_public("get_trades", self._native_params(**locals()))

    async def get_candles(
        self,
        market_id: int,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
        set_timestamp_to_end: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter candlesticks."""
        return await self._native_public("get_candles", self._native_params(**locals()))

    async def get_funding_rates(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter funding rates."""
        return await self._native_public("get_funding_rates", self._native_params(**locals()))

    async def get_fundings(
        self,
        market_id: int,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter historical fundings."""
        return await self._native_public("get_fundings", self._native_params(**locals()))

    async def get_exchange_stats(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter exchange statistics."""
        return await self._native_public("get_exchange_stats", self._native_params(**locals()))

    async def get_execute_stats(self, period: str) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter execution statistics."""
        return await self._native_public("get_execute_stats", self._native_params(**locals()))

    async def get_exchange_metrics(
        self,
        period: str,
        kind: str,
        filter: str | None = None,
        value: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter exchange metrics."""
        return await self._native_public("get_exchange_metrics", self._native_params(**locals()))

    async def get_deposit_networks(self) -> dict[str, Any] | list[Any]:
        """Retrieve supported Lighter deposit networks."""
        return await self._native_public("get_deposit_networks", self._native_params(**locals()))

    async def get_fastbridge_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter fast bridge information."""
        return await self._native_public("get_fastbridge_info", self._native_params(**locals()))

    async def get_layer1_basic_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter layer-1 basic information."""
        return await self._native_public("get_layer1_basic_info", self._native_params(**locals()))

    async def get_lease_options(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account lease options."""
        return await self._native_public("get_lease_options", self._native_params(**locals()))

    async def get_withdrawal_delay(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal delay information."""
        return await self._native_public("get_withdrawal_delay", self._native_params(**locals()))

    async def get_account(
        self,
        by: str,
        value: str,
        active_only: bool | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve public Lighter account data."""
        return await self._native_public("get_account", self._native_params(**locals()))

    async def get_accounts_by_l1_address(
        self,
        l1_address: str,
        cursor: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter accounts tied to an L1 address."""
        return await self._native_public(
            "get_accounts_by_l1_address",
            self._native_params(**locals()),
        )

    async def get_account_metadata(
        self,
        by: str,
        value: str,
        cursor: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account metadata."""
        return await self._native_public("get_account_metadata", self._native_params(**locals()))

    async def get_api_keys(
        self,
        account_index: int,
        api_key_index: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API key metadata."""
        return await self._native_public("get_api_keys", self._native_params(**locals()))

    async def get_public_pools_metadata(
        self,
        index: int,
        limit: int,
        filter: str | None = None,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter public pool metadata."""
        return await self._native_public(
            "get_public_pools_metadata",
            self._native_params(**locals()),
        )

    async def get_pnl(
        self,
        by: str,
        value: str,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
        ignore_transfers: bool | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter PnL data."""
        return await self._native_public("get_pnl", self._native_params(**locals()))

    async def get_asset_details(self, asset_id: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter asset metadata."""
        return await self._native_public("get_asset_details", self._native_params(**locals()))

    async def get_system_config(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter system configuration."""
        return await self._native_public("get_system_config", self._native_params(**locals()))

    async def get_tokens(
        self,
        account_index: int,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account tokens."""
        return await self._native_public("get_tokens", self._native_params(**locals()))

    async def get_token_list(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter token list."""
        return await self._native_public("get_token_list", self._native_params(**locals()))
