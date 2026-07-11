"""Bitget private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for Bitget private account operations."""

    def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Spot maker and taker fee rates."""
        return self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Futures maker and taker fee rates."""
        return self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    def get_all_account_balance(self) -> dict[str, Any]:
        """Retrieve Bitget all-account balance overview."""
        return self._native_private("get_all_account_balance", [])

    def get_funding_assets(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget funding account assets."""
        return self._native_private("get_funding_assets", self._native_params(coin=coin))

    def get_spot_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget spot account information."""
        return self._native_private("get_spot_account_info", [])

    def get_spot_account_assets(
        self,
        coin: str | None = None,
        assetType: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account assets."""
        return self._native_private(
            "get_spot_account_assets",
            self._native_params(coin=coin, assetType=assetType),
        )

    def get_spot_account_bills(
        self,
        coin: str | None = None,
        groupType: str | None = None,
        businessType: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account bills."""
        return self._native_private(
            "get_spot_account_bills",
            self._native_params(
                coin=coin,
                groupType=groupType,
                businessType=businessType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                idLessThan=idLessThan,
            ),
        )

    def transfer(
        self,
        coin: str,
        amount: str,
        fromType: str,
        toType: str,
        symbol: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Transfer assets between Bitget account types."""
        return self._native_private(
            "transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromType=fromType,
                toType=toType,
                symbol=symbol,
                clientOid=clientOid,
            ),
        )

    def get_transfer_records(
        self,
        coin: str,
        fromType: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        clientOid: str | None = None,
        pageNum: int | str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget account transfer records."""
        return self._native_private(
            "get_transfer_records",
            self._native_params(
                coin=coin,
                fromType=fromType,
                startTime=startTime,
                endTime=endTime,
                clientOid=clientOid,
                pageNum=pageNum,
                limit=limit,
                idLessThan=idLessThan,
            ),
        )

    def get_transferable_coins(
        self,
        fromType: str,
        toType: str,
    ) -> dict[str, Any]:
        """Retrieve coins transferable between Bitget account types."""
        return self._native_private(
            "get_transferable_coins",
            self._native_params(fromType=fromType, toType=toType),
        )

    def get_deposit_records(
        self,
        coin: str | None = None,
        orderId: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget deposit records."""
        return self._native_private(
            "get_deposit_records",
            self._native_params(
                coin=coin,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                idLessThan=idLessThan,
                limit=limit,
            ),
        )

    def get_uta_account_assets(self) -> dict[str, Any]:
        """Retrieve Bitget UTA account assets."""
        return self._native_private("get_uta_account_assets", [])

    def get_uta_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget UTA API account information."""
        return self._native_private("get_uta_account_info", [])

    def set_uta_leverage(
        self,
        category: str,
        leverage: str | int,
        product_symbol: str | None = None,
        symbol: str | None = None,
        coin: str | None = None,
        posSide: str | None = None,
        marginMode: str | None = None,
        longLeverage: str | int | None = None,
        shortLeverage: str | int | None = None,
    ) -> dict[str, Any]:
        """Set Bitget UTA leverage."""
        return self._native_private(
            "set_uta_leverage",
            self._native_params(
                category=category,
                leverage=leverage,
                product_symbol=product_symbol,
                symbol=symbol,
                coin=coin,
                posSide=posSide,
                marginMode=marginMode,
                longLeverage=longLeverage,
                shortLeverage=shortLeverage,
            ),
        )

    def set_uta_hold_mode(self, holdMode: str) -> dict[str, Any]:
        """Set Bitget UTA holding mode."""
        return self._native_private(
            "set_uta_hold_mode",
            self._native_params(holdMode=holdMode),
        )

    def get_futures_account(
        self,
        product_symbol: str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures account."""
        return self._native_private(
            "get_futures_account",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
            ),
        )

    def get_futures_accounts(
        self,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures accounts."""
        return self._native_private(
            "get_futures_accounts",
            self._native_params(productType=productType),
        )

    def get_futures_account_bills(
        self,
        productType: str = "USDT-FUTURES",
        symbol: str | None = None,
        marginCoin: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        lastEndId: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures account bills."""
        return self._native_private(
            "get_futures_account_bills",
            self._native_params(
                productType=productType,
                symbol=symbol,
                marginCoin=marginCoin,
                startTime=startTime,
                endTime=endTime,
                lastEndId=lastEndId,
                limit=limit,
            ),
        )

    def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int | str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        holdSide: str | None = None,
    ) -> dict[str, Any]:
        """Set Bitget futures leverage."""
        return self._native_private(
            "set_futures_leverage",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                leverage=leverage,
                holdSide=holdSide,
            ),
        )

    def set_futures_margin_mode(
        self,
        product_symbol: str,
        marginMode: str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures margin mode."""
        return self._native_private(
            "set_futures_margin_mode",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                marginMode=marginMode,
            ),
        )

    def set_futures_position_mode(
        self,
        posMode: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures position mode."""
        return self._native_private(
            "set_futures_position_mode",
            self._native_params(productType=productType, posMode=posMode),
        )

    def get_futures_positions(
        self,
        productType: str = "USDT-FUTURES",
        marginCoin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve all Bitget futures positions."""
        return self._native_private(
            "get_futures_positions",
            self._native_params(productType=productType, marginCoin=marginCoin),
        )

    def get_futures_position(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures position."""
        return self._native_private(
            "get_futures_position",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
            ),
        )
