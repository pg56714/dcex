"""Aster V3 private account HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """HTTP client for Aster V3 private account operations."""

    def _account_symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.ASTER, product_symbol)

    def get_spot_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account information."""
        return self._request("GET", SpotAccount.ACCOUNT)

    def get_spot_transaction_history(
        self,
        asset: str | None = None,
        type_: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account transaction history."""
        return self._request(
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

    def transfer_spot_futures(
        self,
        amount: str,
        asset: str,
        clientTranId: str,
        kindType: str,
        market: str = "spot",
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between the Aster spot and futures wallets."""
        path = SpotAccount.TRANSFER if market.lower() == "spot" else FuturesAccount.TRANSFER
        return self._request(
            "POST",
            path,
            {
                "amount": amount,
                "asset": asset,
                "clientTranId": clientTranId,
                "kindType": kindType,
            },
        )

    def get_futures_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures position mode."""
        return self._request("GET", FuturesAccount.POSITION_MODE)

    def set_futures_position_mode(
        self,
        dualSidePosition: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures position mode."""
        return self._request(
            "POST",
            FuturesAccount.POSITION_MODE,
            {"dualSidePosition": dualSidePosition},
        )

    def get_futures_stp_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures self-trade prevention mode."""
        return self._request("GET", FuturesAccount.STP_MODE)

    def set_futures_stp_mode(self, stpMode: str) -> dict[str, Any] | list[Any]:
        """Change the Aster futures self-trade prevention mode."""
        return self._request("POST", FuturesAccount.STP_MODE, {"stpMode": stpMode})

    def get_futures_multi_assets_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures multi-assets mode."""
        return self._request("GET", FuturesAccount.MULTI_ASSETS_MODE)

    def set_futures_multi_assets_mode(
        self,
        multiAssetsMargin: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures multi-assets mode."""
        return self._request(
            "POST",
            FuturesAccount.MULTI_ASSETS_MODE,
            {"multiAssetsMargin": multiAssetsMargin},
        )

    def get_futures_balance(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account balances."""
        return self._request("GET", FuturesAccount.BALANCE)

    def get_futures_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account information."""
        return self._request("GET", FuturesAccount.ACCOUNT)

    def modify_futures_position_margin(
        self,
        product_symbol: str,
        amount: str,
        type_: int,
        positionSide: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Add or reduce isolated margin on an Aster futures position."""
        return self._request(
            "POST",
            FuturesAccount.POSITION_MARGIN,
            {
                "symbol": self._account_symbol(product_symbol),
                "positionSide": positionSide,
                "amount": amount,
                "type": type_,
            },
        )

    def get_futures_position_margin_history(
        self,
        product_symbol: str,
        type_: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster isolated position-margin history."""
        return self._request(
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

    def get_futures_position_risk(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures position information."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesAccount.POSITION_RISK, {"symbol": symbol})

    def get_futures_user_trades(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account trades."""
        return self._request(
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

    def get_futures_income(
        self,
        product_symbol: str | None = None,
        incomeType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures income history."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return self._request(
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

    def get_futures_leverage_bracket(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures notional and leverage brackets."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesAccount.LEVERAGE_BRACKET, {"symbol": symbol})

    def get_futures_adl_quantile(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures ADL quantile estimates."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return self._request("GET", FuturesAccount.ADL_QUANTILE, {"symbol": symbol})

    def get_futures_force_orders(
        self,
        product_symbol: str | None = None,
        autoCloseType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures liquidation orders for the account."""
        symbol = self._account_symbol(product_symbol) if product_symbol else None
        return self._request(
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

    def get_futures_commission_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures commission rates for the account."""
        return self._request(
            "GET",
            FuturesAccount.COMMISSION_RATE,
            {"symbol": self._account_symbol(product_symbol)},
        )

    def update_futures_mmp(
        self,
        product_symbol: str,
        windowTimeInMilliseconds: int,
        frozenTimeInMilliseconds: int,
        qtyLimit: str | None = None,
        valueLimit: str | None = None,
        deltaLimit: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Configure Aster futures market-maker protection."""
        return self._request(
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

    def get_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures market-maker protection settings."""
        return self._request(
            "GET",
            FuturesAccount.MMP,
            {"symbol": self._account_symbol(product_symbol)},
        )

    def delete_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Delete Aster futures market-maker protection settings."""
        return self._request(
            "DELETE",
            FuturesAccount.MMP,
            {"symbol": self._account_symbol(product_symbol)},
        )

    def reset_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Reset an Aster futures market-maker protection freeze."""
        return self._request(
            "POST",
            FuturesAccount.MMP_RESET,
            {"symbol": self._account_symbol(product_symbol)},
        )

    def create_spot_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster spot user-data listen key."""
        return self._request("POST", SpotAccount.LISTEN_KEY)

    def keep_alive_spot_listen_key(
        self,
        listenKey: str,
    ) -> dict[str, Any] | list[Any]:
        """Extend an Aster spot listen key."""
        return self._request("PUT", SpotAccount.LISTEN_KEY, {"listenKey": listenKey})

    def close_spot_listen_key(self, listenKey: str) -> dict[str, Any] | list[Any]:
        """Close an Aster spot listen key."""
        return self._request("DELETE", SpotAccount.LISTEN_KEY, {"listenKey": listenKey})

    def create_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster futures user-data listen key."""
        return self._request("POST", FuturesAccount.LISTEN_KEY)

    def keep_alive_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Extend an Aster futures listen key."""
        return self._request("PUT", FuturesAccount.LISTEN_KEY)

    def close_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Close an Aster futures listen key."""
        return self._request("DELETE", FuturesAccount.LISTEN_KEY)
