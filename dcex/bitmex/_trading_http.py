"""BitMEX private trading-history HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradingHTTP(HTTPManager):
    """HTTP client for BitMEX trading-history APIs."""

    def get_executions(
        self,
        product_symbol: str | None = None,
        filter: str | None = None,
        columns: str | None = None,
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
        return self._native_private("get_executions", params)

    def get_trade_history(
        self,
        product_symbol: str | None = None,
        filter: str | None = None,
        columns: str | None = None,
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
        return self._native_private("get_trade_history", params)

    def get_trading_volume(self) -> dict[str, Any]:
        """Get BitMEX trading volume information."""
        return self._native_private("get_trading_volume", [])

    def _history_params(
        self,
        *,
        product_symbol: str | None,
        filter: str | None,
        columns: str | None,
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
            params.append(
                (
                    "targetAccountIds[]",
                    self._native_params(targetAccountIds_array=targetAccountIds_array)[0][1],
                )
            )
        return params
