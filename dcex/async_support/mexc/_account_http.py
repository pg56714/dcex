"""MEXC async private account HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import ContractAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """Async HTTP client for MEXC private account APIs."""

    async def get_kyc_status(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC account KYC status."""
        return await self._request("GET", SpotAccount.KYC_STATUS, {"recvWindow": recvWindow})

    async def get_spot_self_symbols(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot symbols enabled for the API key."""
        return await self._request("GET", SpotAccount.SELF_SYMBOLS, {"recvWindow": recvWindow})

    async def get_spot_account(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account balances."""
        return await self._request("GET", SpotAccount.ACCOUNT, {"recvWindow": recvWindow})

    async def get_spot_mx_deduct_status(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC MX deduct status."""
        return await self._request("GET", SpotAccount.MX_DEDUCT_ENABLE, {"recvWindow": recvWindow})

    async def set_spot_mx_deduct(
        self,
        mxDeductEnable: bool,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Enable or disable MEXC MX deduct for spot commission fees."""
        return await self._request(
            "POST",
            SpotAccount.MX_DEDUCT_ENABLE,
            {"mxDeductEnable": mxDeductEnable, "recvWindow": recvWindow},
        )

    async def get_spot_symbol_commission(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot commission for a symbol or all symbols."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            SpotAccount.SYMBOL_COMMISSION,
            {"symbol": symbol, "recvWindow": recvWindow},
        )

    async def get_currency_info(
        self,
        coin: str | None = None,
        network: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC currency information."""
        return await self._request(
            "GET",
            SpotAccount.CURRENCY_INFO,
            {"coin": coin, "network": network, "recvWindow": recvWindow},
        )

    async def get_deposit_history(
        self,
        coin: str | None = None,
        status: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC deposit history."""
        return await self._request(
            "GET",
            SpotAccount.DEPOSIT_HISTORY,
            {
                "coin": coin,
                "status": status,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    async def get_withdraw_history(
        self,
        coin: str | None = None,
        status: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC withdraw history."""
        return await self._request(
            "GET",
            SpotAccount.WITHDRAW_HISTORY,
            {
                "coin": coin,
                "status": status,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    async def get_deposit_address(
        self,
        coin: str,
        network: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC deposit address."""
        return await self._request(
            "GET",
            SpotAccount.DEPOSIT_ADDRESS,
            {"coin": coin, "network": network, "recvWindow": recvWindow},
        )

    async def user_universal_transfer(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between MEXC Spot and Futures accounts."""
        return await self._request(
            "POST",
            SpotAccount.USER_UNIVERSAL_TRANSFER,
            {
                "fromAccountType": fromAccountType,
                "toAccountType": toAccountType,
                "asset": asset,
                "amount": amount,
                "recvWindow": recvWindow,
            },
        )

    async def get_user_universal_transfer_history(
        self,
        fromAccountType: str,
        toAccountType: str,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC universal transfer history."""
        return await self._request(
            "GET",
            SpotAccount.USER_UNIVERSAL_TRANSFER,
            {
                "fromAccountType": fromAccountType,
                "toAccountType": toAccountType,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    async def get_user_universal_transfer_by_id(
        self,
        tranId: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC universal transfer record by tranId."""
        return await self._request(
            "GET",
            SpotAccount.USER_UNIVERSAL_TRANSFER_BY_ID,
            {"tranId": tranId, "recvWindow": recvWindow},
        )

    async def get_internal_transfer_history(
        self,
        tranId: str | None = None,
        clientTranId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC internal transfer history."""
        return await self._request(
            "GET",
            SpotAccount.INTERNAL_TRANSFER_HISTORY,
            {
                "tranId": tranId,
                "clientTranId": clientTranId,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    async def get_contract_assets(self) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Contract account assets."""
        return await self._request("GET", ContractAccount.ASSETS, api="contract")

    async def get_contract_asset(self, currency: str) -> dict[str, Any] | list[Any]:
        """Retrieve one MEXC Contract asset."""
        path = str(ContractAccount.ASSET).format(currency=currency)
        return await self._request("GET", path, api="contract")

    async def get_contract_transfer_records(
        self,
        currency: str | None = None,
        state: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract asset transfer records."""
        return await self._request(
            "GET",
            ContractAccount.TRANSFER_RECORDS,
            {
                "currency": currency,
                "state": state,
                "page_num": page_num,
                "page_size": page_size,
            },
            api="contract",
        )

    async def get_contract_history_positions(
        self,
        product_symbol: str | None = None,
        type_: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical positions."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            ContractAccount.HISTORY_POSITIONS,
            {"symbol": symbol, "type": type_, "page_num": page_num, "page_size": page_size},
            api="contract",
        )

    async def get_contract_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current open positions."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            ContractAccount.OPEN_POSITIONS,
            {"symbol": symbol},
            api="contract",
        )

    async def get_contract_funding_records(
        self,
        product_symbol: str | None = None,
        position_id: str | int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract user funding records."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            ContractAccount.FUNDING_RECORDS,
            {
                "symbol": symbol,
                "position_id": position_id,
                "page_num": page_num,
                "page_size": page_size,
            },
            api="contract",
        )

    async def get_contract_risk_limits(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk limits."""
        return await self._request(
            "GET",
            ContractAccount.RISK_LIMITS,
            {"symbol": self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)},
            api="contract",
        )

    async def get_contract_trading_fee_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trading fee rate."""
        return await self._request(
            "GET",
            ContractAccount.TRADING_FEE_RATE,
            {"symbol": self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)},
            api="contract",
        )

    async def get_contract_leverage(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract leverage."""
        return await self._request(
            "GET",
            ContractAccount.LEVERAGE,
            {"symbol": self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)},
            api="contract",
        )

    async def change_contract_margin(
        self,
        positionId: int,
        amount: str,
        type_: str,
    ) -> dict[str, Any] | list[Any]:
        """Increase or decrease MEXC Contract position margin."""
        return await self._request(
            "POST",
            ContractAccount.CHANGE_MARGIN,
            {"positionId": positionId, "amount": amount, "type": type_},
            api="contract",
        )

    async def change_contract_leverage(
        self,
        leverage: int,
        positionId: int | None = None,
        openType: int | None = None,
        product_symbol: str | None = None,
        positionType: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Change MEXC Contract leverage."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "POST",
            ContractAccount.CHANGE_LEVERAGE,
            {
                "positionId": positionId,
                "leverage": leverage,
                "openType": openType,
                "symbol": symbol,
                "positionType": positionType,
            },
            api="contract",
        )

    async def get_contract_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract position mode."""
        return await self._request("GET", ContractAccount.POSITION_MODE, api="contract")

    async def change_contract_position_mode(
        self,
        positionMode: int,
    ) -> dict[str, Any] | list[Any]:
        """Change MEXC Contract position mode."""
        return await self._request(
            "POST",
            ContractAccount.CHANGE_POSITION_MODE,
            {"positionMode": positionMode},
            api="contract",
        )
