"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    def get_asset_withdraw_vasp_list(self) -> dict[str, Any]:
        """
        GET /v5/asset/withdraw/vasp/list.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/vasp-list.mdx
        """
        return self._native_private("get_asset_withdraw_vasp_list", self._native_params())

    def get_asset_withdraw_query_address(
        self,
        *,
        coin: str | None = None,
        chain: str | None = None,
        address_type: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/asset/withdraw/query-address.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/withdraw-address.mdx
        """
        return self._native_private(
            "get_asset_withdraw_query_address",
            self._native_params(
                coin=coin, chain=chain, addressType=address_type, limit=limit, cursor=cursor
            ),
        )

    def get_asset_withdraw_query_record(
        self,
        *,
        withdraw_id: str | None = None,
        tx_id: str | None = None,
        coin: str | None = None,
        withdraw_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/asset/withdraw/query-record.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/withdraw-record.mdx
        """
        return self._native_private(
            "get_asset_withdraw_query_record",
            self._native_params(
                withdrawID=withdraw_id,
                txID=tx_id,
                coin=coin,
                withdrawType=withdraw_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )


class AssetHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AssetHTTP."""

    def get_withdrawable_amount(self, coin: str) -> dict[str, Any]:
        """Get withdrawable amount for a coin."""
        return self._native_private(
            "get_withdrawable_amount",
            self._native_params(coin=coin),
        )
