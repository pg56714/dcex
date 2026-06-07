"""Bitget private account HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import CommonAccount, FuturesAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """HTTP client for Bitget private account operations."""

    def get_all_account_balance(self) -> dict[str, Any]:
        """Retrieve Bitget all-account balance overview."""
        return self._request("GET", CommonAccount.ALL_ACCOUNT_BALANCE, signed=True)

    def get_funding_assets(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget funding account assets."""
        return self._request("GET", CommonAccount.FUNDING_ASSETS, {"coin": coin}, signed=True)

    def get_spot_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget spot account information."""
        return self._request("GET", SpotAccount.INFO, signed=True)

    def get_spot_account_assets(
        self,
        coin: str | None = None,
        assetType: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account assets."""
        payload: dict[str, Any] = {"coin": coin, "assetType": assetType}
        return self._request("GET", SpotAccount.ASSETS, payload, signed=True)

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
        payload: dict[str, Any] = {
            "coin": coin,
            "groupType": groupType,
            "businessType": businessType,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "idLessThan": idLessThan,
        }
        return self._request("GET", SpotAccount.BILLS, payload, signed=True)

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
        payload: dict[str, Any] = {
            "coin": coin,
            "amount": amount,
            "fromType": fromType,
            "toType": toType,
            "symbol": symbol,
            "clientOid": clientOid,
        }
        return self._request("POST", SpotAccount.TRANSFER, payload, signed=True)

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
        return self._request("GET", SpotAccount.TRANSFER_RECORDS, payload, signed=True)

    def get_transferable_coins(
        self,
        fromType: str,
        toType: str,
    ) -> dict[str, Any]:
        """Retrieve coins transferable between Bitget account types."""
        payload: dict[str, Any] = {"fromType": fromType, "toType": toType}
        return self._request("GET", SpotAccount.TRANSFER_COIN_INFO, payload, signed=True)

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
        payload: dict[str, Any] = {
            "coin": coin,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "idLessThan": idLessThan,
            "limit": limit,
        }
        return self._request("GET", SpotAccount.DEPOSIT_RECORDS, payload, signed=True)

    def get_futures_account(
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
        return self._request("GET", FuturesAccount.ACCOUNT, payload, signed=True)

    def get_futures_accounts(
        self,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures accounts."""
        return self._request(
            "GET", FuturesAccount.ACCOUNTS, {"productType": productType}, signed=True
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
        payload: dict[str, Any] = {
            "productType": productType,
            "symbol": symbol,
            "marginCoin": marginCoin,
            "startTime": startTime,
            "endTime": endTime,
            "lastEndId": lastEndId,
            "limit": limit,
        }
        return self._request("GET", FuturesAccount.BILLS, payload, signed=True)

    def set_futures_leverage(
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
        return self._request("POST", FuturesAccount.SET_LEVERAGE, payload, signed=True)

    def set_futures_margin_mode(
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
        return self._request("POST", FuturesAccount.SET_MARGIN_MODE, payload, signed=True)

    def set_futures_position_mode(
        self,
        posMode: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures position mode."""
        payload: dict[str, Any] = {"productType": productType, "posMode": posMode}
        return self._request("POST", FuturesAccount.SET_POSITION_MODE, payload, signed=True)

    def get_futures_positions(
        self,
        productType: str = "USDT-FUTURES",
        marginCoin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve all Bitget futures positions."""
        payload: dict[str, Any] = {"productType": productType, "marginCoin": marginCoin}
        return self._request("GET", FuturesAccount.ALL_POSITIONS, payload, signed=True)

    def get_futures_position(
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
        return self._request("GET", FuturesAccount.SINGLE_POSITION, payload, signed=True)
