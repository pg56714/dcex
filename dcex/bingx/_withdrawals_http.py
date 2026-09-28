"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    def get_withdrawal_history(
        self,
        *,
        id: str | None = None,
        coin: str | None = None,
        withdraw_order_id: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        tx_id: str | None = None,
        recv_window: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get withdrawal history.

        GET /openApi/api/v3/capital/withdraw/history. Timestamps use milliseconds."""
        return self._native_private(
            "get_withdrawal_history",
            self._native_params(
                id=id,
                coin=coin,
                withdrawOrderId=withdraw_order_id,
                status=status,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                txId=tx_id,
                recvWindow=recv_window,
            ),
        )

    def transfer_master_internal(
        self,
        *,
        coin: str,
        user_account_type: int,
        user_account: str,
        amount: str,
        calling_code: str | None = None,
        wallet_type: int,
        transfer_client_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Transfer master internal.

        POST /openApi/wallets/v1/capital/innerTransfer/apply.

        The English and Chinese docs disagree on the spot walletType code (4/15).
        This wrapper preserves the caller-selected integer without choosing either.
        Source: https://bingx-api.github.io/docs-v3/

        The recipient is a different user. API transfers have no second confirmation;
        they execute on submit. Verify the recipient UID, email, or phone first.
        """
        return self._native_private(
            "transfer_master_internal",
            self._native_params(
                **{
                    "coin": coin,
                    "userAccountType": user_account_type,
                    "userAccount": user_account,
                    "amount": amount,
                    "callingCode": calling_code,
                    "walletType": wallet_type,
                    "transferClientId": transfer_client_id,
                    "recvWindow": recv_window,
                }
            ),
        )

    def transfer_sub_account_internal(
        self,
        *,
        coin: str,
        user_account_type: int,
        user_account: str,
        amount: str,
        calling_code: str | None = None,
        wallet_type: int,
        transfer_client_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Transfer sub account internal.

        POST /openApi/wallets/v1/capital/subAccountInnerTransfer/apply.

        Sub-account-only operation; uses a signed JSON body.
        Source: https://bingx-api.github.io/docs-v3/
        """
        return self._native_private(
            "transfer_sub_account_internal",
            self._native_params(
                **{
                    "coin": coin,
                    "userAccountType": user_account_type,
                    "userAccount": user_account,
                    "amount": amount,
                    "callingCode": calling_code,
                    "walletType": wallet_type,
                    "transferClientId": transfer_client_id,
                    "recvWindow": recv_window,
                }
            ),
        )

    def create_withdrawal(
        self,
        *,
        coin: str,
        network: str | None = None,
        address: str,
        address_tag: str | None = None,
        amount: str,
        wallet_type: int,
        withdraw_order_id: str | None = None,
        vasp_entity_id: str | None = None,
        recipient_last_name: str | None = None,
        recipient_first_name: str | None = None,
        date_ofbirth: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Create withdrawal.

        POST /openApi/wallets/v1/capital/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.
        Supply destination-specific memo and required Travel Rule information.
        The English and Chinese docs disagree on the spot walletType code (4/15).
        This wrapper preserves the caller-selected integer without choosing either.
        Source: https://bingx-api.github.io/docs-v3/
        """
        return self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "coin": coin,
                    "network": network,
                    "address": address,
                    "addressTag": address_tag,
                    "amount": amount,
                    "walletType": wallet_type,
                    "withdrawOrderId": withdraw_order_id,
                    "vaspEntityId": vasp_entity_id,
                    "recipientLastName": recipient_last_name,
                    "recipientFirstName": recipient_first_name,
                    "dateOfbirth": date_ofbirth,
                    "recvWindow": recv_window,
                }
            ),
        )
