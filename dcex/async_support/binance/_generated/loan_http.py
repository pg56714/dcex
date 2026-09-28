"""Generated binance loan HTTP methods."""

from json import dumps
from typing import Any

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedLoanHTTP(MarketHTTP, TradeHTTP):
    """Loan API methods."""

    async def get_borrow_interest_rate(
        self, *, loan_coin: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Borrow Interest Rate (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-borrow-interest-rate
        """
        return await self._native_private(
            "get_borrow_interest_rate",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"loanCoin": loan_coin, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )

    async def get_collateral_asset_data(
        self, *, collateral_coin: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Collateral Asset Data (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-collateral-asset-data
        """
        return await self._native_private(
            "get_collateral_asset_data",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "collateralCoin": collateral_coin,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    async def get_loanable_assets_data(
        self,
        *,
        loan_coin: str | None = None,
        vip_level: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Loanable Assets Data (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-loanable-assets-data
        """
        return await self._native_private(
            "get_loanable_assets_data",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanCoin": loan_coin,
                    "vipLevel": vip_level,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    async def query_application_status(
        self,
        *,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Application Status (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#query-application-status
        """
        return await self._native_private(
            "query_application_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )
