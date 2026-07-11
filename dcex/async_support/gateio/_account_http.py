from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Gate.io async account HTTP client backed by Rust private dispatch."""

    async def get_spot_fee_rates(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve current Gate.io Spot maker and taker fee rates."""
        return await self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_fee_rates(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve current Gate.io Futures maker and taker fee rates."""
        return await self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_total_balance(self, currency: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_total_balance",
            self._native_params(currency=currency),
        )

    async def wallet_transfer(
        self,
        currency: str,
        from_account: str,
        to_account: str,
        amount: str,
        currency_pair: str | None = None,
        settle: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "wallet_transfer",
            self._native_params(
                currency=currency,
                from_=from_account,
                to=to_account,
                amount=amount,
                currency_pair=currency_pair,
                settle=settle,
            ),
        )

    async def get_unified_accounts(
        self,
        currency: str | None = None,
        sub_uid: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_unified_accounts",
            self._native_params(currency=currency, sub_uid=sub_uid),
        )

    async def get_futures_account(self, ccy: str = "usdt") -> dict[str, Any]:
        return await self._native_private(
            "get_futures_account",
            self._native_params(ccy=ccy),
        )

    async def get_futures_account_book(
        self,
        ccy: str = "usdt",
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        change_type: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_futures_account_book",
            self._native_params(
                ccy=ccy,
                contract=contract,
                limit=limit,
                offset=offset,
                from_time=from_time,
                to_time=to_time,
                change_type=change_type,
            ),
        )

    async def get_delivery_account(self, ccy: str = "usdt") -> dict[str, Any]:
        return await self._native_private(
            "get_delivery_account",
            self._native_params(ccy=ccy),
        )

    async def get_delivery_account_book(
        self,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        change_type: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_delivery_account_book",
            self._native_params(
                ccy=ccy,
                limit=limit,
                offset=offset,
                from_time=from_time,
                to_time=to_time,
                change_type=change_type,
            ),
        )

    async def get_spot_account(self, ccy: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_account",
            self._native_params(ccy=ccy),
        )

    async def get_spot_account_book(
        self,
        ccy: str | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        type_: str | None = None,
        code: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_account_book",
            self._native_params(
                ccy=ccy,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                page=page,
                limit=limit,
                type_=type_,
                code=code,
            ),
        )

    async def get_spot_fee(self, product_symbol: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_fee",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_spot_batch_fee(
        self,
        product_symbols: list[str] | tuple[str, ...] | str,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_batch_fee",
            self._native_params(product_symbols=product_symbols),
        )
