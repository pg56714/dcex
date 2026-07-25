"""BitMEX async private trading-history HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradingHTTP(HTTPManager):
    """Async HTTP client for BitMEX trading-history APIs."""

    async def get_executions(
        self,
        product_symbol: str | None = None,
        pool: str | None = None,
        filter: dict[str, Any] | str | None = None,
        columns: list[str] | str | None = None,
        count: int = 100,
        start: int = 0,
        reverse: bool = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str | int] | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX execution history."""
        params = self._history_params(
            product_symbol=product_symbol,
            pool=pool,
            filter=filter,
            columns=columns,
            count=count,
            start=start,
            reverse=reverse,
            startTime=startTime,
            endTime=endTime,
            targetAccountId=targetAccountId,
            targetAccountIds=targetAccountIds,
            targetAccountIds_array=targetAccountIds_array,
        )
        return await self._native_private("get_executions", params)

    async def get_trade_history(
        self,
        product_symbol: str | None = None,
        pool: str | None = None,
        filter: dict[str, Any] | str | None = None,
        columns: list[str] | str | None = None,
        count: int = 100,
        start: int = 0,
        reverse: bool = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str | int] | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX trade history."""
        params = self._history_params(
            product_symbol=product_symbol,
            pool=pool,
            filter=filter,
            columns=columns,
            count=count,
            start=start,
            reverse=reverse,
            startTime=startTime,
            endTime=endTime,
            targetAccountId=targetAccountId,
            targetAccountIds=targetAccountIds,
            targetAccountIds_array=targetAccountIds_array,
        )
        return await self._native_private("get_trade_history", params)

    async def get_trading_volume(self) -> dict[str, Any]:
        """Get BitMEX trading volume information."""
        return await self._native_private("get_trading_volume", [])

    def _history_params(
        self,
        *,
        product_symbol: str | None,
        pool: str | None,
        filter: dict[str, Any] | str | None,
        columns: list[str] | str | None,
        count: int,
        start: int,
        reverse: bool,
        startTime: str | None,
        endTime: str | None,
        targetAccountId: int | None,
        targetAccountIds: str | None,
        targetAccountIds_array: list[str | int] | None,
    ) -> list[tuple[str, str]]:
        params = self._native_params(
            product_symbol=product_symbol,
            pool=pool,
            filter=filter,
            columns=columns,
            count=count,
            start=start,
            reverse=reverse,
            startTime=startTime,
            endTime=endTime,
            targetAccountId=targetAccountId,
            targetAccountIds=targetAccountIds,
        )
        if targetAccountIds_array is not None:
            params.extend(
                ("targetAccountIds[]", str(account_id)) for account_id in targetAccountIds_array
            )
        return params
