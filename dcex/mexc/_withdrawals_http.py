"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

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


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    def get_withdrawal_addresses(
        self, *, coin: str | None = None, page: int | None = None, limit: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v3/capital/withdraw/address.
        """
        return self._native_private(
            "get_withdrawal_addresses", self._native_params(coin=coin, page=page, limit=limit)
        )

    def get_rebate_affiliate_withdraw(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v3/rebate/affiliate/withdraw.

        Source: https://www.mexc.com/api-docs/spot-v3/rebate-endpoints/get-affiliate-withdraw-record-affiliate-only
        """
        return self._native_private(
            "get_rebate_affiliate_withdraw",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "page": page,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }
            ),
        )

    def cancel_spot_withdrawal(
        self,
        *,
        id: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        DELETE /api/v3/capital/withdraw.

        Source: https://www.mexc.com/api-docs/spot-v3/wallet-endpoints/cancel-withdraw
        """
        return self._native_private(
            "cancel_spot_withdrawal",
            self._native_params(
                **{
                    "id": id,
                    "recvWindow": recv_window,
                }
            ),
        )

    def create_spot_withdrawal(
        self,
        *,
        coin: str,
        withdraw_order_id: str | None = None,
        network: str | None = None,
        contract_address: str | None = None,
        address: str,
        memo: str | None = None,
        amount: str,
        remark: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v3/capital/withdraw.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://www.mexc.com/api-docs/spot-v3/wallet-endpoints/withdrawnew
        """
        return self._native_private(
            "create_spot_withdrawal",
            self._native_params(
                **{
                    "coin": coin,
                    "withdrawOrderId": withdraw_order_id,
                    "netWork": network,
                    "contractAddress": contract_address,
                    "address": address,
                    "memo": memo,
                    "amount": amount,
                    "remark": remark,
                    "recvWindow": recv_window,
                }
            ),
        )

    def create_spot_withdrawal_legacy(
        self,
        *,
        coin: str,
        withdraw_order_id: str | None = None,
        network: str | None = None,
        address: str,
        memo: str | None = None,
        amount: str,
        remark: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v3/capital/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.
        Legacy endpoint; the exchange documents that it will be taken offline.
        Source: https://www.mexc.com/api-docs/spot-v3/wallet-endpoints/withdrawpreviousoffline-soon
        """
        return self._native_private(
            "create_spot_withdrawal_legacy",
            self._native_params(
                **{
                    "coin": coin,
                    "withdrawOrderId": withdraw_order_id,
                    "network": network,
                    "address": address,
                    "memo": memo,
                    "amount": amount,
                    "remark": remark,
                    "recvWindow": recv_window,
                }
            ),
        )
