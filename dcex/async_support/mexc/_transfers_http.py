"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    async def user_universal_transfer(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between MEXC Spot and Futures accounts."""
        return await self._native_private(
            "user_universal_transfer",
            self._native_params(
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                asset=asset,
                amount=amount,
                recvWindow=recvWindow,
            ),
        )

    async def transfer_subaccount_assets(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        fromAccount: str | None = None,
        toAccount: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets among a MEXC master account and its sub-accounts."""
        return await self._native_private(
            "transfer_subaccount_assets",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                asset=asset,
                amount=amount,
                recvWindow=recvWindow,
            ),
        )

    async def get_subaccount_transfer_history(
        self,
        fromAccountType: str,
        toAccountType: str,
        fromAccount: str | None = None,
        toAccount: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC master/sub-account universal-transfer history."""
        return await self._native_private(
            "get_subaccount_transfer_history",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                startTime=startTime,
                endTime=endTime,
                page=page,
                limit=limit,
                recvWindow=recvWindow,
            ),
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
        return await self._native_private(
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

    async def get_user_universal_transfer_by_id(
        self,
        tranId: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC universal transfer record by tranId."""
        return await self._native_private(
            "get_user_universal_transfer_by_id",
            self._native_params(tranId=tranId, recvWindow=recvWindow),
        )

    async def get_internal_transfer_history(
        self,
        tranId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC internal transfer history."""
        return await self._native_private(
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

    async def get_contract_transfer_records(
        self,
        currency: str | None = None,
        state: str | None = None,
        type_: str | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract asset transfer records."""
        return await self._native_private(
            "get_contract_transfer_records",
            self._native_params(
                currency=currency,
                state=state,
                type_=type_,
                page_num=page_num,
                page_size=page_size,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    async def transfer_spot_internal(
        self,
        *,
        to_account_type: str,
        to_account: str,
        area_code: str | None = None,
        asset: str,
        amount: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v3/capital/transfer/internal.

        Source: https://www.mexc.com/api-docs/spot-v3/wallet-endpoints/internal-transfer


        The recipient is a different user. API transfers have no second confirmation;
        they execute on submit. Verify the recipient UID, email, or phone first.
        """
        return await self._native_private(
            "transfer_spot_internal",
            self._native_params(
                **{
                    "toAccountType": to_account_type,
                    "toAccount": to_account,
                    "areaCode": area_code,
                    "asset": asset,
                    "amount": amount,
                    "recvWindow": recv_window,
                }
            ),
        )
