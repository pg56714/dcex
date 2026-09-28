"""Generated kucoin withdrawals HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedWithdrawalsHTTP(TradeHTTP):
    """Withdrawals API methods."""

    async def post_v2_broker_withdrawal(self, *, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Apply for Fast Withdrawal.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/apply-for-fast-withdrawal
        API withdrawals have no second confirmation; they execute on submit.
        This Fast API may return validation factors; submit them only if required
        by the exchange. The incomplete official schema is forwarded as a body object.
        """
        return await self._native_private(
            "post_v2_broker_withdrawal", self._native_params(body=body)
        )

    async def get_v3_broker_nd_withdraw_detail(self, *, withdrawal_id: str) -> Any:  # noqa: ANN401
        """
        Get Withdraw Detail.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-withdraw-detail
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_withdraw_detail", self._native_params(withdrawalId=withdrawal_id)
        )

    async def get_v1_copy_trade_futures_position_margin_max_withdraw_margin(
        self, *, symbol: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Max Withdraw Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-max-withdraw-margin
        """
        return await self._native_private(
            "get_v1_copy_trade_futures_position_margin_max_withdraw_margin",
            self._native_params(symbol=symbol, positionSide=position_side),
        )

    async def post_v1_copy_trade_futures_position_margin_withdraw_margin(
        self, *, symbol: str, withdraw_amount: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Remove Isolated Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/remove-isolated-margin
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_margin_withdraw_margin",
            self._native_params(
                symbol=symbol, withdrawAmount=withdraw_amount, positionSide=position_side
            ),
        )
