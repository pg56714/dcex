"""Extended account HTTP client backed by Rust."""

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
        type: str | None = None,  # noqa: A002
        status: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get deposit, withdrawal, and transfer history."""
        return self._native_private(
            "get_asset_operations",
            self._native_params(type=type, status=status, cursor=cursor, limit=limit),
        )

    def get_spot_balances(self, accountId: int | str | None = None) -> Any:  # noqa: N803, ANN401
        query = {} if accountId is None else {"accountId": accountId}
        return self._request("GET", "/api/v1/user/spot/balances", query, signed=True)

    def get_positions(self, market: str | None = None, side: str | None = None) -> Any:  # noqa: ANN401
        return self._native_private(
            "get_positions",
            self._native_params(market=market, side=side),
        )

    def get_positions_history(
        self,
        market: str | None = None,
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
        market: str | None = None,
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
        market: str | None = None,
        side: str | None = None,
        startTime: int | None = None,  # noqa: N803
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

    def get_leverage(self, market: str | None = None) -> Any:  # noqa: ANN401
        return self._native_private("get_leverage", self._native_params(market=market))

    def get_fees(
        self,
        market: str | None = None,
        builderId: int | str | None = None,  # noqa: N803
    ) -> Any:  # noqa: ANN401
        query = {
            key: value
            for key, value in {"market": market, "builderId": builderId}.items()
            if value is not None
        }
        return self._request("GET", "/api/v1/user/fees", query, signed=True)

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
