"""BitMEX async private order HTTP client backed by Rust."""
# ruff: noqa: ASYNC109

from typing import Any

from ...enums import OrderSide
from ...utils.common import Common
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for BitMEX private order APIs."""

    async def place_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderQty: int | None = None,
        ordType: str = "Limit",
        price: float | None = None,
        stopPx: float | None = None,
        clOrdID: str | None = None,
        clOrdLinkID: str | None = None,
        contingencyType: str | None = None,
        displayQty: int | None = None,
        execInst: str | None = None,
        pegOffsetValue: float | None = None,
        pegPriceType: str | None = None,
        timeInForce: str | None = None,
        text: str | None = None,
        targetAccountId: int | None = None,
        expiryTime: str | None = None,
        maxSlippagePct: float | None = None,
    ) -> dict[str, Any]:
        """Place a new BitMEX order."""
        return await self._native_private(
            "place_order",
            self._native_params(
                product_symbol=product_symbol,
                side=OrderSide.from_any(side).to_exchange(Common.BITMEX),
                orderQty=orderQty,
                ordType=ordType,
                price=price,
                stopPx=stopPx,
                clOrdID=clOrdID,
                clOrdLinkID=clOrdLinkID,
                contingencyType=contingencyType,
                displayQty=displayQty,
                execInst=execInst,
                pegOffsetValue=pegOffsetValue,
                pegPriceType=pegPriceType,
                timeInForce=timeInForce,
                text=text,
                targetAccountId=targetAccountId,
                expiryTime=expiryTime,
                maxSlippagePct=maxSlippagePct,
            ),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX market order."""
        return await self._native_private(
            "place_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=OrderSide.from_any(side).to_exchange(Common.BITMEX),
                orderQty=orderQty,
                clOrdID=clOrdID,
            ),
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX market buy order."""
        return await self._native_private(
            "place_market_buy_order",
            self._native_params(product_symbol=product_symbol, orderQty=orderQty, clOrdID=clOrdID),
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX market sell order."""
        return await self._native_private(
            "place_market_sell_order",
            self._native_params(product_symbol=product_symbol, orderQty=orderQty, clOrdID=clOrdID),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        timeInForce: str = "GoodTillCancel",
    ) -> dict[str, Any]:
        """Place a BitMEX limit order."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=OrderSide.from_any(side).to_exchange(Common.BITMEX),
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
                timeInForce=timeInForce,
            ),
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX limit buy order."""
        return await self._native_private(
            "place_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
            ),
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX limit sell order."""
        return await self._native_private(
            "place_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
            ),
        )

    async def place_post_only_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        execInst: str = "ParticipateDoNotInitiate",
    ) -> dict[str, Any]:
        """Place a BitMEX post-only order."""
        return await self._native_private(
            "place_post_only_order",
            self._native_params(
                product_symbol=product_symbol,
                side=OrderSide.from_any(side).to_exchange(Common.BITMEX),
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
                execInst=execInst,
            ),
        )

    async def place_post_only_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX post-only buy order."""
        return await self._native_private(
            "place_post_only_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
            ),
        )

    async def place_post_only_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMEX post-only sell order."""
        return await self._native_private(
            "place_post_only_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                orderQty=orderQty,
                price=price,
                clOrdID=clOrdID,
            ),
        )

    async def amend_order(
        self,
        orderID: str | None = None,
        origClOrdID: str | None = None,
        product_symbol: str | None = None,
        clOrdID: str | None = None,
        leavesQty: int | None = None,
        orderQty: int | None = None,
        price: float | None = None,
        stopPx: float | None = None,
        pegOffsetValue: float | None = None,
        text: str | None = None,
        targetAccountId: int | None = None,
    ) -> dict[str, Any]:
        """Amend a BitMEX order."""
        if orderID is None and origClOrdID is None:
            raise ValueError("Either orderID or origClOrdID must be provided")
        return await self._native_private(
            "amend_order",
            self._native_params(
                orderID=orderID,
                origClOrdID=origClOrdID,
                product_symbol=product_symbol,
                clOrdID=clOrdID,
                leavesQty=leavesQty,
                orderQty=orderQty,
                price=price,
                stopPx=stopPx,
                pegOffsetValue=pegOffsetValue,
                text=text,
                targetAccountId=targetAccountId,
            ),
        )

    async def cancel_order(
        self,
        orderID: str | list[str] | None = None,
        clOrdID: str | list[str] | None = None,
        targetAccountId: int | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """Cancel one or more BitMEX orders."""
        return await self._native_private(
            "cancel_order",
            self._native_params(
                orderID=orderID,
                clOrdID=clOrdID,
                targetAccountId=targetAccountId,
                text=text,
            ),
        )

    async def cancel_all_orders(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: list[str | int] | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all BitMEX orders."""
        return await self._native_private(
            "cancel_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                filter=filter,
                targetAccountId=targetAccountId,
                targetAccountIds=targetAccountIds,
                text=text,
            ),
        )

    async def set_cancel_all_after(
        self, timeout: int, targetAccountId: int | None = None
    ) -> dict[str, Any]:  # noqa: ASYNC109
        """Set BitMEX's order cancel-all dead-man switch timeout in milliseconds."""
        return await self._native_private(
            "set_cancel_all_after",
            self._native_params(timeout=timeout, targetAccountId=targetAccountId),
        )

    async def get_order(
        self,
        product_symbol: str | None = None,
        targetAccountId: int | None = None,
        filter: str | None = None,
        columns: str | None = None,
        count: int | None = 100,
        start: int | None = 0,
        reverse: bool | None = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str | int] | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX order information."""
        params = self._native_params(
            product_symbol=product_symbol,
            targetAccountId=targetAccountId,
            filter=filter,
            columns=columns,
            count=count,
            start=start,
            reverse=reverse,
            startTime=startTime,
            endTime=endTime,
            targetAccountIds=targetAccountIds,
        )
        if targetAccountIds_array is not None:
            params.append(
                (
                    "targetAccountIds[]",
                    self._native_params(targetAccountIds_array=targetAccountIds_array)[0][1],
                )
            )
        return await self._native_private("get_order", params)
