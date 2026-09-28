"""Generated kucoin transfers HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedTransfersHTTP(TradeHTTP):
    """Transfers API methods."""

    async def post_v1_broker_nd_transfer(
        self,
        *,
        currency: str,
        amount: str,
        direction: str,
        account_type: str,
        special_uid: str,
        special_account_type: str,
        client_oid: str,
    ) -> Any:  # noqa: ANN401
        """
        Transfer.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/transfer
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "post_v1_broker_nd_transfer",
            self._native_params(
                currency=currency,
                amount=amount,
                direction=direction,
                accountType=account_type,
                specialUid=special_uid,
                specialAccountType=special_account_type,
                clientOid=client_oid,
            ),
        )

    async def get_v3_broker_nd_transfer_detail(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Get Transfer History.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-transfer-history
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_transfer_detail", self._native_params(orderId=order_id)
        )
