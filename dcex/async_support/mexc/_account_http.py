"""MEXC private account async HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AccountHTTPTransfersHTTP
from ._withdrawals_http import AccountHTTPWithdrawalsHTTP


class AccountHTTP(AccountHTTPWithdrawalsHTTP, AccountHTTPTransfersHTTP, HTTPManager):
    """Async HTTP client for MEXC private account APIs."""

    async def get_kyc_status(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC account KYC status."""
        return await self._native_private(
            "get_kyc_status",
            self._native_params(recvWindow=recvWindow),
        )

    async def get_spot_self_symbols(
        self, recvWindow: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot symbols enabled for the API key."""
        return await self._native_private(
            "get_spot_self_symbols",
            self._native_params(recvWindow=recvWindow),
        )

    async def get_spot_account(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account balances."""
        return await self._native_private(
            "get_spot_account",
            self._native_params(recvWindow=recvWindow),
        )

    async def get_spot_mx_deduct_status(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC MX deduct status."""
        return await self._native_private(
            "get_spot_mx_deduct_status",
            self._native_params(recvWindow=recvWindow),
        )

    async def set_spot_mx_deduct(
        self,
        mxDeductEnable: bool,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Enable or disable MEXC MX deduct for spot commission fees."""
        return await self._native_private(
            "set_spot_mx_deduct",
            self._native_params(mxDeductEnable=mxDeductEnable, recvWindow=recvWindow),
        )

    async def get_spot_symbol_commission(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot commission for a symbol."""
        return await self._native_private(
            "get_spot_symbol_commission",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    async def get_currency_info(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC currency information."""
        return await self._native_private(
            "get_currency_info",
            self._native_params(recvWindow=recvWindow),
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
        return await self._native_private(
            "get_deposit_history",
            self._native_params(
                coin=coin,
                status=status,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def get_deposit_address(
        self,
        coin: str,
        network: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC deposit address."""
        return await self._native_private(
            "get_deposit_address",
            self._native_params(coin=coin, network=network, recvWindow=recvWindow),
        )

    async def get_subaccounts(
        self,
        subAccount: str | None = None,
        isFreeze: bool | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC sub-accounts for the master account."""
        return await self._native_private(
            "get_subaccounts",
            self._native_params(
                subAccount=subAccount,
                isFreeze=isFreeze,
                page=page,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def get_subaccount_asset(
        self,
        subAccount: str,
        accountType: str = "SPOT",
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve the Spot assets of one MEXC sub-account."""
        return await self._native_private(
            "get_subaccount_asset",
            self._native_params(
                subAccount=subAccount,
                accountType=accountType,
                recvWindow=recvWindow,
            ),
        )

    async def get_contract_assets(self) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Contract account assets."""
        return await self._native_private("get_contract_assets", [])

    async def get_contract_asset(self, currency: str) -> dict[str, Any] | list[Any]:
        """Retrieve one MEXC Contract asset."""
        return await self._native_private(
            "get_contract_asset",
            self._native_params(currency=currency),
        )

    async def get_contract_history_positions(
        self,
        product_symbol: str | None = None,
        type_: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        position_type: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical positions."""
        return await self._native_private(
            "get_contract_history_positions",
            self._native_params(
                product_symbol=product_symbol,
                type_=type_,
                start_time=start_time,
                end_time=end_time,
                position_type=position_type,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_open_positions(
        self,
        product_symbol: str | None = None,
        positionId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current open positions."""
        return await self._native_private(
            "get_contract_open_positions",
            self._native_params(product_symbol=product_symbol, positionId=positionId),
        )

    async def get_contract_funding_records(
        self,
        product_symbol: str | None = None,
        position_id: str | int | None = None,
        position_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract user funding records."""
        return await self._native_private(
            "get_contract_funding_records",
            self._native_params(
                product_symbol=product_symbol,
                position_id=position_id,
                position_type=position_type,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_risk_limits(
        self, product_symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk limits."""
        return await self._native_private(
            "get_contract_risk_limits",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_contract_trading_fee_rate(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trading fee rate."""
        return await self._native_private(
            "get_contract_trading_fee_rate",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_contract_leverage(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract leverage."""
        return await self._native_private(
            "get_contract_leverage",
            self._native_params(product_symbol=product_symbol),
        )

    async def change_contract_margin(
        self,
        positionId: int,
        amount: str,
        type_: str,
    ) -> dict[str, Any] | list[Any]:
        """Increase or decrease MEXC Contract position margin."""
        return await self._native_private(
            "change_contract_margin",
            self._native_params(positionId=positionId, amount=amount, type_=type_),
        )

    async def change_contract_leverage(
        self,
        leverage: int,
        positionId: int | None = None,
        openType: int | None = None,
        product_symbol: str | None = None,
        positionType: int | None = None,
        leverageMode: int | None = None,
        marginSelected: bool | None = None,
        leverageSelected: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Change MEXC Contract leverage."""
        return await self._native_private(
            "change_contract_leverage",
            self._native_params(
                leverage=leverage,
                positionId=positionId,
                openType=openType,
                product_symbol=product_symbol,
                positionType=positionType,
                leverageMode=leverageMode,
                marginSelected=marginSelected,
                leverageSelected=leverageSelected,
            ),
        )

    async def get_contract_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract position mode."""
        return await self._native_private("get_contract_position_mode", [])

    async def change_contract_position_mode(self, positionMode: int) -> dict[str, Any] | list[Any]:
        """Change MEXC Contract position mode."""
        return await self._native_private(
            "change_contract_position_mode",
            self._native_params(positionMode=positionMode),
        )

    async def change_contract_multi_asset_mode(self, enabled: bool) -> dict[str, Any] | list[Any]:
        """Enable or disable MEXC cross-asset futures collateral mode."""
        return await self._native_private(
            "change_contract_multi_asset_mode",
            self._native_params(isMultiAssetMode=str(enabled).lower()),
        )

    async def change_contract_auto_add_margin(
        self, positionId: str | int, enabled: bool
    ) -> dict[str, Any] | list[Any]:
        """Enable or disable auto-add margin for an isolated futures position."""
        return await self._native_private(
            "change_contract_auto_add_margin",
            self._native_params(positionId=positionId, isEnabled=str(enabled).lower()),
        )
