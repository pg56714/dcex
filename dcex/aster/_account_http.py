"""Aster V3 private account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for Aster V3 private account operations."""

    def get_spot_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account information."""
        return self._native_private("get_spot_account", [])

    def get_spot_transaction_history(
        self,
        asset: str | None = None,
        type_: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account transaction history."""
        return self._native_private(
            "get_spot_transaction_history",
            self._native_params(
                asset=asset,
                type_=type_,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
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
        return self._native_private(
            "transfer_spot_futures",
            self._native_params(
                amount=amount,
                asset=asset,
                clientTranId=clientTranId,
                kindType=kindType,
                market=market,
            ),
        )

    def get_futures_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures position mode."""
        return self._native_private("get_futures_position_mode", [])

    def set_futures_position_mode(
        self,
        dualSidePosition: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures position mode."""
        return self._native_private(
            "set_futures_position_mode",
            self._native_params(dualSidePosition=dualSidePosition),
        )

    def get_futures_stp_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures self-trade prevention mode."""
        return self._native_private("get_futures_stp_mode", [])

    def set_futures_stp_mode(self, stpMode: str) -> dict[str, Any] | list[Any]:
        """Change the Aster futures self-trade prevention mode."""
        return self._native_private(
            "set_futures_stp_mode",
            self._native_params(stpMode=stpMode),
        )

    def get_futures_multi_assets_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve the current Aster futures multi-assets mode."""
        return self._native_private("get_futures_multi_assets_mode", [])

    def set_futures_multi_assets_mode(
        self,
        multiAssetsMargin: bool,
    ) -> dict[str, Any] | list[Any]:
        """Change the Aster futures multi-assets mode."""
        return self._native_private(
            "set_futures_multi_assets_mode",
            self._native_params(multiAssetsMargin=multiAssetsMargin),
        )

    def get_futures_balance(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account balances."""
        return self._native_private("get_futures_balance", [])

    def get_futures_account(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account information."""
        return self._native_private("get_futures_account", [])

    def modify_futures_position_margin(
        self,
        product_symbol: str,
        amount: str,
        type_: int,
        positionSide: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Add or reduce isolated margin on an Aster futures position."""
        return self._native_private(
            "modify_futures_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                positionSide=positionSide,
                amount=amount,
                type_=type_,
            ),
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
        return self._native_private(
            "get_futures_position_margin_history",
            self._native_params(
                product_symbol=product_symbol,
                type_=type_,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_futures_position_risk(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures position information."""
        return self._native_private(
            "get_futures_position_risk",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_user_trades(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures account trades."""
        return self._native_private(
            "get_futures_user_trades",
            self._native_params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                fromId=fromId,
                limit=limit,
            ),
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
        return self._native_private(
            "get_futures_income",
            self._native_params(
                product_symbol=product_symbol,
                incomeType=incomeType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_futures_leverage_bracket(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures notional and leverage brackets."""
        return self._native_private(
            "get_futures_leverage_bracket",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_adl_quantile(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures ADL quantile estimates."""
        return self._native_private(
            "get_futures_adl_quantile",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_force_orders(
        self,
        product_symbol: str | None = None,
        autoCloseType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures liquidation orders for the account."""
        return self._native_private(
            "get_futures_force_orders",
            self._native_params(
                product_symbol=product_symbol,
                autoCloseType=autoCloseType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_futures_commission_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures commission rates for the account."""
        return self._native_private(
            "get_futures_commission_rate",
            self._native_params(product_symbol=product_symbol),
        )

    def update_futures_mmp(
        self,
        product_symbol: str,
        windowTimeInMilliseconds: int,
        frozenTimeInMilliseconds: int,
        qtyLimit: int | None = None,
        valueLimit: int | None = None,
        deltaLimit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Configure Aster futures market-maker protection."""
        return self._native_private(
            "update_futures_mmp",
            self._native_params(
                product_symbol=product_symbol,
                windowTimeInMilliseconds=windowTimeInMilliseconds,
                frozenTimeInMilliseconds=frozenTimeInMilliseconds,
                qtyLimit=qtyLimit,
                valueLimit=valueLimit,
                deltaLimit=deltaLimit,
            ),
        )

    def get_futures_mmp(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures market-maker protection settings."""
        return self._native_private(
            "get_futures_mmp",
            self._native_params(product_symbol=product_symbol),
        )

    def delete_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Delete Aster futures market-maker protection settings."""
        return self._native_private(
            "delete_futures_mmp",
            self._native_params(product_symbol=product_symbol),
        )

    def reset_futures_mmp(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Reset an Aster futures market-maker protection freeze."""
        return self._native_private(
            "reset_futures_mmp",
            self._native_params(product_symbol=product_symbol),
        )

    def create_spot_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster spot user-data listen key."""
        return self._native_private("create_spot_listen_key", [])

    def keep_alive_spot_listen_key(
        self,
        listenKey: str,
    ) -> dict[str, Any] | list[Any]:
        """Extend an Aster spot listen key."""
        return self._native_private(
            "keep_alive_spot_listen_key",
            self._native_params(listenKey=listenKey),
        )

    def close_spot_listen_key(self, listenKey: str) -> dict[str, Any] | list[Any]:
        """Close an Aster spot listen key."""
        return self._native_private(
            "close_spot_listen_key",
            self._native_params(listenKey=listenKey),
        )

    def create_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Create an Aster futures user-data listen key."""
        return self._native_private("create_futures_listen_key", [])

    def keep_alive_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Extend an Aster futures listen key."""
        return self._native_private("keep_alive_futures_listen_key", [])

    def close_futures_listen_key(self) -> dict[str, Any] | list[Any]:
        """Close an Aster futures listen key."""
        return self._native_private("close_futures_listen_key", [])
