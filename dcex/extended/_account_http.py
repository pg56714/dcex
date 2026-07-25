"""Extended account HTTP client backed by Rust."""

from collections.abc import Sequence
from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for Extended account endpoints."""

    def get_account_details(self) -> Any:  # noqa: ANN401
        return self._native_private("get_account_details", [])

    def get_sub_accounts(self) -> Any:  # noqa: ANN401
        return self._native_private("get_sub_accounts", [])

    def get_balance(self) -> Any:  # noqa: ANN401
        return self._native_private("get_balance", [])

    def get_asset_operations(
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
        return self._native_private(
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

    def get_spot_balances(
        self,
        accountId: int | Sequence[int] | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_spot_balances",
            self._native_params(accountId=accountId),
        )

    def get_positions(
        self,
        market: str | Sequence[str] | None = None,
        side: str | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_positions",
            self._native_params(market=market, side=side),
        )

    def get_positions_history(
        self,
        market: str | Sequence[str] | None = None,
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_positions_history",
            self._native_params(market=market, side=side, cursor=cursor, limit=limit),
        )

    def get_trades_history(
        self,
        market: str | Sequence[str] | None = None,
        type: str | None = None,  # noqa: A002
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_trades_history",
            self._native_params(
                market=market,
                type=type,
                side=side,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_funding_payments(
        self,
        startTime: int,  # noqa: N803
        market: str | Sequence[str] | None = None,
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_funding_payments",
            self._native_params(
                market=market,
                side=side,
                startTime=startTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_leverage(self, market: str | Sequence[str] | None = None) -> Any:  # noqa: ANN401
        return self._native_private("get_leverage", self._native_params(market=market))

    def get_fees(
        self,
        market: str | Sequence[str] | None = None,
        builderId: int | str | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_fees",
            self._native_params(market=market, builderId=builderId),
        )

    def get_rebates(self) -> Any:  # noqa: ANN401
        """Get account rebate statistics."""
        return self._native_private("get_rebates", [])

    def get_builder_dashboard(self) -> Any:  # noqa: ANN401
        """Get statistics for the authenticated builder."""
        return self._native_private("get_builder_dashboard", [])

    def get_builder_trades(
        self,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get trade history for the authenticated builder."""
        return self._native_private(
            "get_builder_trades",
            self._native_params(cursor=cursor, limit=limit),
        )

    def get_bridge_config(self) -> Any:  # noqa: ANN401
        """Get chains supported by the Extended bridge."""
        return self._native_private("get_bridge_config", [])

    def get_bridge_quote(
        self,
        chainIn: str,  # noqa: N803
        chainOut: str,  # noqa: N803
        amount: str | int | float,
        asset: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Get a non-binding bridge quote."""
        return self._native_private(
            "get_bridge_quote",
            self._native_params(
                chainIn=chainIn,
                chainOut=chainOut,
                amount=amount,
                asset=asset,
            ),
        )
