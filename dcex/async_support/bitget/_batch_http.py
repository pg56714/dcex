"""Fund movement and batch endpoint mixins."""

from typing import Any

from ..._keyword_aliases import legacy_keywords
from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    @legacy_keywords({"orderList": "order_list", "batchMode": "batch_mode"})
    async def place_spot_batch_orders(
        self,
        order_list: list[dict[str, Any]],
        product_symbol: str | None = None,
        batch_mode: str | None = None,
    ) -> dict[str, Any]:
        """Place Bitget spot orders in batch."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batch_mode,
                orderList=order_list,
            ),
        )

    @legacy_keywords({"orderList": "order_list", "batchMode": "batch_mode"})
    async def cancel_spot_batch_orders(
        self,
        order_list: list[dict[str, Any]],
        product_symbol: str | None = None,
        batch_mode: str | None = None,
    ) -> dict[str, Any]:
        """Cancel Bitget spot orders in batch."""
        return await self._native_private(
            "cancel_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batch_mode,
                orderList=order_list,
            ),
        )

    @legacy_keywords({"orderList": "order_list"})
    async def place_uta_batch_orders(self, order_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Place Bitget UTA orders in batch."""
        return await self._native_private(
            "place_uta_batch_orders",
            self._native_params(orderList=order_list),
        )

    @legacy_keywords({"orderList": "order_list"})
    async def cancel_uta_batch_orders(self, order_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel Bitget UTA orders in batch."""
        return await self._native_private(
            "cancel_uta_batch_orders",
            self._native_params(orderList=order_list),
        )

    @legacy_keywords(
        {
            "orderList": "order_list",
            "productType": "product_type",
            "marginMode": "margin_mode",
            "marginCoin": "margin_coin",
        }
    )
    async def place_futures_batch_orders(
        self,
        order_list: list[dict[str, Any]],
        product_symbol: str,
        product_type: str = "USDT-FUTURES",
        margin_mode: str = "crossed",
        margin_coin: str = "USDT",
    ) -> dict[str, Any]:
        """Place Bitget futures orders in batch."""
        return await self._native_private(
            "place_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginMode=margin_mode,
                marginCoin=margin_coin,
                orderList=order_list,
            ),
        )

    @legacy_keywords(
        {"orderIdList": "order_id_list", "productType": "product_type", "marginCoin": "margin_coin"}
    )
    async def cancel_futures_batch_orders(
        self,
        product_symbol: str | None = None,
        order_id_list: list[dict[str, Any]] | None = None,
        product_type: str = "USDT-FUTURES",
        margin_coin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel Bitget futures orders in batch."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                orderIdList=order_id_list,
            ),
        )

    async def place_cross_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/batch-place-order``."""
        return await self._native_private(
            "place_cross_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderList=orders),
        )

    async def place_isolated_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/batch-place-order``."""
        return await self._native_private(
            "place_isolated_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderList=orders),
        )

    async def cancel_cross_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/batch-cancel-order``."""
        return await self._native_private(
            "cancel_cross_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderIdList=orders),
        )

    async def cancel_isolated_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/batch-cancel-order``."""
        return await self._native_private(
            "cancel_isolated_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderIdList=orders),
        )

    async def batch_cancel_replace_spot_orders(
        self, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/batch-cancel-replace-order``."""
        return await self._native_private(
            "batch_cancel_replace_spot_orders", self._native_params(orderList=orders)
        )

    async def modify_uta_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/batch-modify-order``. At most 20 orders in one category; ACK
        does not confirm matching-engine completion.
        """
        return await self._native_private(
            "modify_uta_batch_orders", self._native_params(orders=orders)
        )

    async def batch_create_classic_sub_accounts(
        self, accounts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create 1..5 virtual sub-accounts and API keys using an array body."""
        return await self._native_private(
            "batch_create_classic_sub_accounts", self._native_params(accounts=accounts)
        )
