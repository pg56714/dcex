"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    async def get_uta_account_max_withdrawal(self, *, coin: str) -> dict[str, Any]:
        """
        GET /api/v3/account/max-withdrawal. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/assets-balance#get-max-withdrawal
        """
        return await self._native_private(
            "get_uta_account_max_withdrawal", self._native_params(coin=coin)
        )

    async def get_classic_spot_wallet_withdrawal_records(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        client_oid: str | None = None,
        id_less_than: str | None = None,
        order_id: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/spot/wallet/withdrawal-records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-withdrawal-records
        """
        return await self._native_private(
            "get_classic_spot_wallet_withdrawal_records",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                clientOid=client_oid,
                idLessThan=id_less_than,
                orderId=order_id,
                limit=limit,
            ),
        )

    async def get_uta_account_withdrawal_records(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        order_id: str | None = None,
        client_oid: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v3/account/withdrawal-records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdrawal-records
        """
        return await self._native_private(
            "get_uta_account_withdrawal_records",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                orderId=order_id,
                clientOid=client_oid,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_account_withdraw_address(
        self,
        *,
        coin: str | None = None,
        type_: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v3/account/withdraw-address. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdraw-address-book
        """
        return await self._native_private(
            "get_uta_account_withdraw_address",
            self._native_params(coin=coin, type=type_, limit=limit, cursor=cursor),
        )

    async def create_spot_withdrawal(
        self,
        *,
        coin: str,
        transfer_type: str,
        address: str,
        size: str,
        chain: str | None = None,
        inner_to_type: str | None = None,
        area_code: str | None = None,
        tag: str | None = None,
        remark: str | None = None,
        client_oid: str | None = None,
        member_code: str | None = None,
        identity_type: str | None = None,
        company_name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Withdraw.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#withdraw
        """
        return await self._native_private(
            "create_spot_withdrawal",
            self._native_params(
                coin=coin,
                transferType=transfer_type,
                address=address,
                chain=chain,
                innerToType=inner_to_type,
                areaCode=area_code,
                tag=tag,
                size=size,
                remark=remark,
                clientOid=client_oid,
                memberCode=member_code,
                identityType=identity_type,
                companyName=company_name,
                firstName=first_name,
                lastName=last_name,
            ),
        )

    async def cancel_spot_withdrawal(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Cancel Withdrawal.

        Cancellation is subject to the exchange withdrawal state.
        Source: https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#cancel-withdrawal
        """
        return await self._native_private(
            "cancel_spot_withdrawal", self._native_params(orderId=order_id)
        )

    async def create_uta_withdrawal(
        self,
        *,
        coin: str,
        transfer_type: str,
        address: str,
        size: str,
        chain: str | None = None,
        inner_to_type: str | None = None,
        area_code: str | None = None,
        tag: str | None = None,
        remark: str | None = None,
        client_oid: str | None = None,
        member_code: str | None = None,
        identity_type: str | None = None,
        company_name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        account_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#withdrawal
        """
        return await self._native_private(
            "create_uta_withdrawal",
            self._native_params(
                coin=coin,
                chain=chain,
                transferType=transfer_type,
                address=address,
                innerToType=inner_to_type,
                areaCode=area_code,
                tag=tag,
                size=size,
                remark=remark,
                clientOid=client_oid,
                memberCode=member_code,
                identityType=identity_type,
                companyName=company_name,
                firstName=first_name,
                lastName=last_name,
                accountType=account_type,
            ),
        )

    async def cancel_uta_withdrawal(
        self, *, order_id: str | None = None, client_oid: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Cancel Withdrawal.

        Cancellation is subject to the exchange withdrawal state.
        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#cancel-withdrawal
        """
        return await self._native_private(
            "cancel_uta_withdrawal", self._native_params(orderId=order_id, clientOid=client_oid)
        )
