"""MEXC private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for MEXC private account APIs."""

    def get_kyc_status(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC account KYC status."""
        return self._native_private("get_kyc_status", self._native_params(recvWindow=recvWindow))

    def get_spot_self_symbols(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot symbols enabled for the API key."""
        return self._native_private(
            "get_spot_self_symbols",
            self._native_params(recvWindow=recvWindow),
        )

    def get_spot_account(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account balances."""
        return self._native_private("get_spot_account", self._native_params(recvWindow=recvWindow))

    def get_spot_mx_deduct_status(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC MX deduct status."""
        return self._native_private(
            "get_spot_mx_deduct_status",
            self._native_params(recvWindow=recvWindow),
        )

    def set_spot_mx_deduct(
        self,
        mxDeductEnable: bool,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Enable or disable MEXC MX deduct for spot commission fees."""
        return self._native_private(
            "set_spot_mx_deduct",
            self._native_params(mxDeductEnable=mxDeductEnable, recvWindow=recvWindow),
        )

    def get_spot_symbol_commission(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot commission for a symbol."""
        return self._native_private(
            "get_spot_symbol_commission",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    def get_currency_info(self, recvWindow: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC currency information."""
        return self._native_private(
            "get_currency_info",
            self._native_params(recvWindow=recvWindow),
        )

    def get_deposit_history(
        self,
        coin: str | None = None,
        status: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC deposit history."""
        return self._native_private(
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

    def get_withdraw_history(
        self,
        coin: str | None = None,
        status: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC withdraw history."""
        return self._native_private(
            "get_withdraw_history",
            self._native_params(
                coin=coin,
                status=status,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_deposit_address(
        self,
        coin: str,
        network: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC deposit address."""
        return self._native_private(
            "get_deposit_address",
            self._native_params(coin=coin, network=network, recvWindow=recvWindow),
        )

    def user_universal_transfer(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between MEXC Spot and Futures accounts."""
        return self._native_private(
            "user_universal_transfer",
            self._native_params(
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                asset=asset,
                amount=amount,
                recvWindow=recvWindow,
            ),
        )

    def get_user_universal_transfer_history(
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
        return self._native_private(
            "get_user_universal_transfer_history",
            self._native_params(
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                startTime=startTime,
                endTime=endTime,
                page=page,
                size=size,
                recvWindow=recvWindow,
            ),
        )

    def get_user_universal_transfer_by_id(
        self,
        tranId: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC universal transfer record by tranId."""
        return self._native_private(
            "get_user_universal_transfer_by_id",
            self._native_params(tranId=tranId, recvWindow=recvWindow),
        )

    def get_internal_transfer_history(
        self,
        tranId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC internal transfer history."""
        return self._native_private(
            "get_internal_transfer_history",
            self._native_params(
                tranId=tranId,
                startTime=startTime,
                endTime=endTime,
                page=page,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_contract_assets(self) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Contract account assets."""
        return self._native_private("get_contract_assets", [])

    def get_contract_asset(self, currency: str) -> dict[str, Any] | list[Any]:
        """Retrieve one MEXC Contract asset."""
        return self._native_private(
            "get_contract_asset",
            self._native_params(currency=currency),
        )

    def get_contract_transfer_records(
        self,
        currency: str | None = None,
        state: str | None = None,
        type_: str | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract asset transfer records."""
        return self._native_private(
            "get_contract_transfer_records",
            self._native_params(
                currency=currency,
                state=state,
                type_=type_,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_contract_history_positions(
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
        return self._native_private(
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

    def get_contract_open_positions(
        self,
        product_symbol: str | None = None,
        positionId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current open positions."""
        return self._native_private(
            "get_contract_open_positions",
            self._native_params(product_symbol=product_symbol, positionId=positionId),
        )

    def get_contract_funding_records(
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
        return self._native_private(
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

    def get_contract_risk_limits(
        self, product_symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk limits."""
        return self._native_private(
            "get_contract_risk_limits",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_trading_fee_rate(
        self, product_symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trading fee rate."""
        return self._native_private(
            "get_contract_trading_fee_rate",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_leverage(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract leverage."""
        return self._native_private(
            "get_contract_leverage",
            self._native_params(product_symbol=product_symbol),
        )

    def change_contract_margin(
        self,
        positionId: int,
        amount: str,
        type_: str,
    ) -> dict[str, Any] | list[Any]:
        """Increase or decrease MEXC Contract position margin."""
        return self._native_private(
            "change_contract_margin",
            self._native_params(positionId=positionId, amount=amount, type_=type_),
        )

    def change_contract_leverage(
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
        return self._native_private(
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

    def get_contract_position_mode(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract position mode."""
        return self._native_private("get_contract_position_mode", [])

    def change_contract_position_mode(self, positionMode: int) -> dict[str, Any] | list[Any]:
        """Change MEXC Contract position mode."""
        return self._native_private(
            "change_contract_position_mode",
            self._native_params(positionMode=positionMode),
        )
