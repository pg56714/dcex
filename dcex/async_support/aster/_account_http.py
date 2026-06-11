"""Aster V3 private account async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """HTTP client for Aster V3 private account operations."""

    def _account_symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.ASTER, product_symbol)

    async def get_spot_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account information."""
        return await self._request("GET", SpotAccount.ACCOUNT)

    async def get_spot_transaction_history(
        self,
        asset: str | None = None,
        type_: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account transaction history."""
        return await self._request(
            "GET",
            SpotAccount.TRANSACTION_HISTORY,
            {
                "asset": asset,
                "type": type_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def transfer_spot_futures(
        self,
        amount: str,
        asset: str,
        clientTranId: str,
        kindType: str,
        market: str = "spot",
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between the Aster spot and futures wallets."""
        path = SpotAccount.TRANSFER if market.lower() == "spot" else FuturesAccount.TRANSFER
        return await self._request(
            "POST",
            path,
            {
                "amount": amount,
                "asset": asset,
                "clientTranId": clientTranId,
                "kindType": kindType,
            },
        )

    async def get_futures_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures position mode."""
        return await self._request("GET", FuturesAccount.POSITION_MODE)

    async def set_futures_position_mode(
        self,
        dualSidePosition: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures position mode."""
        return await self._request(
            "POST",
            FuturesAccount.POSITION_MODE,
            {"dualSidePosition": dualSidePosition},
        )

    async def get_futures_stp_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures self-trade prevention mode."""
        return await self._request("GET", FuturesAccount.STP_MODE)

    async def set_futures_stp_mode(self, stpMode: str) -> dict[str, Any] | list[Any]:
        """Change the Aster futures self-trade prevention mode."""
        return await self._request("POST", FuturesAccount.STP_MODE, {"stpMode": stpMode})

    async def get_futures_multi_assets_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures multi-assets mode."""
        return await self._request("GET", FuturesAccount.MULTI_ASSETS_MODE)

    async def set_futures_multi_assets_mode(
        self,
        multiAssetsMargin: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures multi-assets mode."""
        return await self._request(
            "POST",
            FuturesAccount.MULTI_ASSETS_MODE,
            {"multiAssetsMargin": multiAssetsMargin},
        )

    async def get_futures_balance(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account balances."""
        return await self._request("GET", FuturesAccount.BALANCE)

    async def get_futures_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account information."""
        return await self._request("GET", FuturesAccount.ACCOUNT)

    async def modify_futures_position_margin(
        self,
        product_symbol: str,
        amount: str,
        type_: int,
        positionSide: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Add or reduce isolated margin on an Aster futures position."""
        return await self._request(
            "POST",
            FuturesAccount.POSITION_MARGIN,
            {
                "symbol": self._account_symbol(product_symbol),
                "positionSide": positionSide,
                "amount": amount,
                "type": type_,
            },
        )

    async def get_futures_position_margin_history(
        self,
        product_symbol: str,
        type_: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster isolated position-margin history."""
        return await self._request(
            "GET",
            FuturesAccount.POSITION_MARGIN_HISTORY,
            {
                "symbol": self._account_symbol(product_symbol),
                "type": type_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def get_futures_position_risk(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures position information."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return await self._request("GET", FuturesAccount.POSITION_RISK, {"symbol": symbol})

    async def get_futures_user_trades(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account trades."""
        return await self._request(
            "GET",
            FuturesAccount.USER_TRADES,
            {
                "symbol": self._account_symbol(product_symbol),
                "startTime": startTime,
                "endTime": endTime,
                "fromId": fromId,
                "limit": limit,
            },
        )

    async def get_futures_income(
        self,
        product_symbol: str | None = None,
        incomeType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures income history."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return await self._request(
            "GET",
            FuturesAccount.INCOME,
            {
                "symbol": symbol,
                "incomeType": incomeType,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def get_futures_leverage_bracket(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures notional and leverage brackets."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return await self._request("GET", FuturesAccount.LEVERAGE_BRACKET, {"symbol": symbol})

    async def get_futures_adl_quantile(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures ADL quantile estimates."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return await self._request("GET", FuturesAccount.ADL_QUANTILE, {"symbol": symbol})

    async def get_futures_force_orders(
        self,
        product_symbol: str | None = None,
        autoCloseType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures liquidation orders for the account."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return await self._request(
            "GET",
            FuturesAccount.FORCE_ORDERS,
            {
                "symbol": symbol,
                "autoCloseType": autoCloseType,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def get_futures_commission_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures commission rates for the account."""
        return await self._request(
            "GET",
            FuturesAccount.COMMISSION_RATE,
            {"symbol": self._account_symbol(product_symbol)},
        )

    async def update_futures_mmp(
        self,
        product_symbol: str,
        windowTimeInMilliseconds: int,
        frozenTimeInMilliseconds: int,
        qtyLimit: str | None = None,
        valueLimit: str | None = None,
        deltaLimit: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Configure Aster futures market-maker protection."""
        return await self._request(
            "POST",
            FuturesAccount.MMP,
            {
                "symbol": self._account_symbol(product_symbol),
                "windowTimeInMilliseconds": windowTimeInMilliseconds,
                "frozenTimeInMilliseconds": frozenTimeInMilliseconds,
                "qtyLimit": qtyLimit,
                "valueLimit": valueLimit,
                "deltaLimit": deltaLimit,
            },
        )

    async def get_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures market-maker protection settings."""
        return await self._request(
            "GET",
            FuturesAccount.MMP,
            {"symbol": self._account_symbol(product_symbol)},
        )

    async def delete_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Delete Aster futures market-maker protection settings."""
        return await self._request(
            "DELETE",
            FuturesAccount.MMP,
            {"symbol": self._account_symbol(product_symbol)},
        )

    async def reset_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Reset an Aster futures market-maker protection freeze."""
        return await self._request(
            "POST",
            FuturesAccount.MMP_RESET,
            {"symbol": self._account_symbol(product_symbol)},
        )

    async def create_spot_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster spot user-data listen key."""
        return await self._request("POST", SpotAccount.LISTEN_KEY)

    async def keep_alive_spot_listen_key(
        self,
        listenKey: str,
    ) -> dict[str, Any] | list[Any]:
        """Extend an Aster spot listen key."""
        return await self._request("PUT", SpotAccount.LISTEN_KEY, {"listenKey": listenKey})

    async def close_spot_listen_key(self, listenKey: str) -> dict[str, Any] | list[Any]:
        """Close an Aster spot listen key."""
        return await self._request("DELETE", SpotAccount.LISTEN_KEY, {"listenKey": listenKey})

    async def create_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster futures user-data listen key."""
        return await self._request("POST", FuturesAccount.LISTEN_KEY)

    async def keep_alive_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Extend an Aster futures listen key."""
        return await self._request("PUT", FuturesAccount.LISTEN_KEY)

    async def close_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Close an Aster futures listen key."""
        return await self._request("DELETE", FuturesAccount.LISTEN_KEY)
