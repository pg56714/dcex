"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    async def get_transfer_quotas(
        self,
        currency: str,
        account_type: str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable balance for one KuCoin account type."""
        return await self._native_private(
            "get_transfer_quotas",
            self._native_params(currency=currency, account_type=account_type, tag=tag),
        )

    async def flex_transfer(
        self,
        currency: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
        clientOid: str | None = None,
        transfer_type: str = "INTERNAL",
        fromUserId: str | None = None,
        toUserId: str | None = None,
        fromAccountTag: str | None = None,
        toAccountTag: str | None = None,
    ) -> dict[str, Any]:
        """Transfer funds between KuCoin account types."""
        return await self._native_private(
            "flex_transfer",
            self._native_params(
                currency=currency,
                amount=amount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                clientOid=clientOid,
                transfer_type=transfer_type,
                fromUserId=fromUserId,
                toUserId=toUserId,
                fromAccountTag=fromAccountTag,
                toAccountTag=toAccountTag,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    async def transfer_uta_accounts(
        self,
        client_oid: str,
        transfer_type: str,
        currency: str,
        amount: str,
        from_account_type: str,
        from_account_tag: str,
        to_account_type: str,
        to_account_tag: str,
        *,
        from_uid: str | None = None,
        to_uid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/ua/v2/account/transfer``."""
        return await self._native_private(
            "transfer_uta_accounts",
            self._native_params(
                clientOid=client_oid,
                transferType=transfer_type,
                currency=currency,
                amount=amount,
                fromUid=from_uid,
                fromAccountType=from_account_type,
                fromAccountTag=from_account_tag,
                toUid=to_uid,
                toAccountType=to_account_type,
                toAccountTag=to_account_tag,
            ),
        )

    async def get_uta_transfer_quota(
        self, account_type: str, currency: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/transfer-quota``."""
        return await self._native_private(
            "get_uta_transfer_quota",
            self._native_params(
                accountType=account_type, currency=currency, product_symbol=product_symbol
            ),
        )

    async def set_uta_sub_account_transfer_permission(
        self, *, sub_uids: str, sub_to_sub: bool
    ) -> dict[str, Any]:
        """

        POST /api/ua/v2/sub-account/canTransferOut.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/transfer-permission

        """
        return await self._native_private(
            "set_uta_sub_account_transfer_permission",
            self._native_params(subUids=sub_uids, subToSub=sub_to_sub),
        )
