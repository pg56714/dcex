"""Bitget private account async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import CommonAccount, FuturesAccount, SpotAccount, UtaAccount


class AccountHTTP(HTTPManager):
    """Async HTTP client for Bitget private account operations."""

    async def get_all_account_balance(self) -> dict[str, Any]:
        """Retrieve Bitget all-account balance overview."""
        return await self._request("GET", CommonAccount.ALL_ACCOUNT_BALANCE, signed=True)

    async def get_funding_assets(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget funding account assets."""
        return await self._request(
            "GET",
            CommonAccount.FUNDING_ASSETS,
            {"coin": coin},
            signed=True,
        )

    async def get_spot_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget spot account information."""
        return await self._request("GET", SpotAccount.INFO, signed=True)

    async def get_spot_account_assets(
        self,
        coin: str | None = None,
        assetType: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account assets."""
        payload: dict[str, Any] = {"coin": coin, "assetType": assetType}
        return await self._request("GET", SpotAccount.ASSETS, payload, signed=True)

    async def get_spot_account_bills(
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
        payload: dict[str, Any] = {
            "coin": coin,
            "groupType": groupType,
            "businessType": businessType,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "idLessThan": idLessThan,
        }
        return await self._request("GET", SpotAccount.BILLS, payload, signed=True)

    async def transfer(
        self,
        coin: str,
        amount: str,
        fromType: str,
        toType: str,
        symbol: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Transfer assets between Bitget account types."""
        payload: dict[str, Any] = {
            "coin": coin,
            "amount": amount,
            "fromType": fromType,
            "toType": toType,
            "symbol": symbol,
            "clientOid": clientOid,
        }
        return await self._request("POST", SpotAccount.TRANSFER, payload, signed=True)

    async def get_transfer_records(
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
        payload: dict[str, Any] = {
            "coin": coin,
            "fromType": fromType,
            "startTime": startTime,
            "endTime": endTime,
            "clientOid": clientOid,
            "pageNum": pageNum,
            "limit": limit,
            "idLessThan": idLessThan,
        }
        return await self._request("GET", SpotAccount.TRANSFER_RECORDS, payload, signed=True)

    async def get_transferable_coins(
        self,
        fromType: str,
        toType: str,
    ) -> dict[str, Any]:
        """Retrieve coins transferable between Bitget account types."""
        payload: dict[str, Any] = {"fromType": fromType, "toType": toType}
        return await self._request("GET", SpotAccount.TRANSFER_COIN_INFO, payload, signed=True)

    async def get_deposit_records(
        self,
        coin: str | None = None,
        orderId: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget deposit records."""
        payload: dict[str, Any] = {
            "coin": coin,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "idLessThan": idLessThan,
            "limit": limit,
        }
        return await self._request("GET", SpotAccount.DEPOSIT_RECORDS, payload, signed=True)

    async def get_uta_account_assets(self) -> dict[str, Any]:
        """Retrieve Bitget UTA account assets."""
        return await self._request("GET", UtaAccount.ASSETS, signed=True)

    async def get_uta_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget UTA API account information."""
        return await self._request("GET", UtaAccount.INFO, signed=True)

    async def set_uta_leverage(
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
        payload: dict[str, Any] = {
            "category": category,
            "symbol": symbol
            or (
                self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
                if product_symbol is not None
                else None
            ),
            "leverage": str(leverage),
            "coin": coin,
            "posSide": posSide,
            "marginMode": marginMode,
            "longLeverage": str(longLeverage) if longLeverage is not None else None,
            "shortLeverage": str(shortLeverage) if shortLeverage is not None else None,
        }
        return await self._request("POST", UtaAccount.SET_LEVERAGE, payload, signed=True)

    async def set_uta_hold_mode(self, holdMode: str) -> dict[str, Any]:
        """Set Bitget UTA holding mode."""
        return await self._request(
            "POST",
            UtaAccount.SET_HOLD_MODE,
            {"holdMode": holdMode},
            signed=True,
        )

    async def get_futures_account(
        self,
        product_symbol: str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures account."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
        }
        return await self._request("GET", FuturesAccount.ACCOUNT, payload, signed=True)

    async def get_futures_accounts(
        self,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures accounts."""
        return await self._request(
            "GET",
            FuturesAccount.ACCOUNTS,
            {"productType": productType},
            signed=True,
        )

    async def get_futures_account_bills(
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
        payload: dict[str, Any] = {
            "productType": productType,
            "symbol": symbol,
            "marginCoin": marginCoin,
            "startTime": startTime,
            "endTime": endTime,
            "lastEndId": lastEndId,
            "limit": limit,
        }
        return await self._request("GET", FuturesAccount.BILLS, payload, signed=True)

    async def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int | str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        holdSide: str | None = None,
    ) -> dict[str, Any]:
        """Set Bitget futures leverage."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
            "leverage": leverage,
            "holdSide": holdSide,
        }
        return await self._request("POST", FuturesAccount.SET_LEVERAGE, payload, signed=True)

    async def set_futures_margin_mode(
        self,
        product_symbol: str,
        marginMode: str,
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures margin mode."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
            "marginMode": marginMode,
        }
        return await self._request("POST", FuturesAccount.SET_MARGIN_MODE, payload, signed=True)

    async def set_futures_position_mode(
        self,
        posMode: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures position mode."""
        payload: dict[str, Any] = {"productType": productType, "posMode": posMode}
        return await self._request("POST", FuturesAccount.SET_POSITION_MODE, payload, signed=True)

    async def get_futures_positions(
        self,
        productType: str = "USDT-FUTURES",
        marginCoin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve all Bitget futures positions."""
        payload: dict[str, Any] = {"productType": productType, "marginCoin": marginCoin}
        return await self._request("GET", FuturesAccount.ALL_POSITIONS, payload, signed=True)

    async def get_futures_position(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures position."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
        }
        return await self._request("GET", FuturesAccount.SINGLE_POSITION, payload, signed=True)
