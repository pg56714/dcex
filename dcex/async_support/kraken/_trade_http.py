"""Kraken private trade async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """Async HTTP client for Kraken private trading operations."""

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        ordertype: str,
        volume: str,
        price: str | None = None,
        price2: str | None = None,
        leverage: str | None = None,
        oflags: str | None = None,
        timeinforce: str | None = None,
        expiretm: str | None = None,
        starttm: str | None = None,
        reduce_only: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot order."""
        payload: dict[str, Any] = {
            "pair": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "type": side,
            "ordertype": ordertype,
            "volume": volume,
            "price": price,
            "price2": price2,
            "leverage": leverage,
            "oflags": oflags,
            "timeinforce": timeinforce,
            "expiretm": expiretm,
            "starttm": starttm,
            "reduce_only": reduce_only,
            "userref": userref,
            "cl_ord_id": cl_ord_id,
            "validate": validate,
        }
        return await self._request("POST", SpotTrade.ADD_ORDER, query=payload, signed=True)

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market order."""
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            ordertype="market",
            volume=volume,
            cl_ord_id=cl_ord_id,
            validate=validate,
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market buy order."""
        return await self.place_spot_market_order(
            product_symbol, "buy", volume, cl_ord_id, validate
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market sell order."""
        return await self.place_spot_market_order(
            product_symbol,
            "sell",
            volume,
            cl_ord_id,
            validate,
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        oflags: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit order."""
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            ordertype="limit",
            volume=volume,
            price=price,
            timeinforce=timeinforce,
            oflags=oflags,
            cl_ord_id=cl_ord_id,
            validate=validate,
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit buy order."""
        return await self.place_spot_limit_order(
            product_symbol,
            "buy",
            volume,
            price,
            timeinforce,
            None,
            cl_ord_id,
            validate,
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit sell order."""
        return await self.place_spot_limit_order(
            product_symbol,
            "sell",
            volume,
            price,
            timeinforce,
            None,
            cl_ord_id,
            validate,
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit order."""
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side=side,
            volume=volume,
            price=price,
            oflags="post",
            cl_ord_id=cl_ord_id,
            validate=validate,
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit buy order."""
        return await self.place_spot_post_only_limit_order(
            product_symbol,
            "buy",
            volume,
            price,
            cl_ord_id,
            validate,
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit sell order."""
        return await self.place_spot_post_only_limit_order(
            product_symbol,
            "sell",
            volume,
            price,
            cl_ord_id,
            validate,
        )

    async def get_spot_open_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot open orders."""
        payload: dict[str, Any] = {"trades": trades, "userref": userref, "cl_ord_id": cl_ord_id}
        return await self._request("POST", SpotTrade.OPEN_ORDERS, query=payload, signed=True)

    async def get_spot_closed_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        closetime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot closed orders."""
        payload: dict[str, Any] = {
            "trades": trades,
            "userref": userref,
            "start": start,
            "end": end,
            "ofs": ofs,
            "closetime": closetime,
        }
        return await self._request("POST", SpotTrade.CLOSED_ORDERS, query=payload, signed=True)

    async def get_spot_orders(
        self,
        txid: str,
        trades: bool | None = None,
        userref: int | None = None,
    ) -> dict[str, Any]:
        """Query Kraken spot order info by transaction id."""
        payload: dict[str, Any] = {"txid": txid, "trades": trades, "userref": userref}
        return await self._request("POST", SpotTrade.QUERY_ORDERS, query=payload, signed=True)

    async def get_spot_trade_history(
        self,
        type_: str | None = None,
        trades: bool | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        without_count: bool | None = None,
        consolidate_taker: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trades/fills history."""
        payload: dict[str, Any] = {
            "type": type_,
            "trades": trades,
            "start": start,
            "end": end,
            "ofs": ofs,
            "without_count": without_count,
            "consolidate_taker": consolidate_taker,
        }
        return await self._request("POST", SpotTrade.TRADES_HISTORY, query=payload, signed=True)

    async def cancel_spot_order(
        self,
        txid: str | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken spot order."""
        if txid is None and userref is None and cl_ord_id is None:
            raise ValueError("Specify txid, userref, or cl_ord_id.")
        payload: dict[str, Any] = {"txid": txid, "userref": userref, "cl_ord_id": cl_ord_id}
        return await self._request("POST", SpotTrade.CANCEL_ORDER, query=payload, signed=True)

    async def cancel_spot_all_orders(self) -> dict[str, Any]:
        """Cancel all Kraken spot open orders."""
        return await self._request("POST", SpotTrade.CANCEL_ALL, signed=True)

    async def place_futures_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: int | str,
        limitPrice: str | None = None,
        stopPrice: str | None = None,
        cliOrdId: str | None = None,
        triggerSignal: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures order."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "side": side,
            "orderType": orderType,
            "size": size,
            "limitPrice": limitPrice,
            "stopPrice": stopPrice,
            "cliOrdId": cliOrdId,
            "triggerSignal": triggerSignal,
            "reduceOnly": reduceOnly,
        }
        return await self._request(
            "POST",
            FuturesTrade.SEND_ORDER,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    async def place_futures_market_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market order."""
        return await self.place_futures_order(
            product_symbol=product_symbol,
            side=side,
            orderType="mkt",
            size=size,
            cliOrdId=cliOrdId,
            reduceOnly=reduceOnly,
        )

    async def place_futures_market_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market buy order."""
        return await self.place_futures_market_order(
            product_symbol,
            "buy",
            size,
            cliOrdId,
            reduceOnly,
        )

    async def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market sell order."""
        return await self.place_futures_market_order(
            product_symbol,
            "sell",
            size,
            cliOrdId,
            reduceOnly,
        )

    async def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit order."""
        return await self.place_futures_order(
            product_symbol=product_symbol,
            side=side,
            orderType="lmt",
            size=size,
            limitPrice=price,
            cliOrdId=cliOrdId,
            reduceOnly=reduceOnly,
        )

    async def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit buy order."""
        return await self.place_futures_limit_order(
            product_symbol,
            "buy",
            size,
            price,
            cliOrdId,
            reduceOnly,
        )

    async def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit sell order."""
        return await self.place_futures_limit_order(
            product_symbol,
            "sell",
            size,
            price,
            cliOrdId,
            reduceOnly,
        )

    async def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit order."""
        return await self.place_futures_order(
            product_symbol=product_symbol,
            side=side,
            orderType="post",
            size=size,
            limitPrice=price,
            cliOrdId=cliOrdId,
            reduceOnly=reduceOnly,
        )

    async def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit buy order."""
        return await self.place_futures_post_only_limit_order(
            product_symbol,
            "buy",
            size,
            price,
            cliOrdId,
            reduceOnly,
        )

    async def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit sell order."""
        return await self.place_futures_post_only_limit_order(
            product_symbol,
            "sell",
            size,
            price,
            cliOrdId,
            reduceOnly,
        )

    async def get_futures_open_orders(self) -> dict[str, Any]:
        """Retrieve Kraken Futures open orders."""
        return await self._request(
            "GET",
            FuturesTrade.OPEN_ORDERS,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    async def get_futures_order_status(
        self,
        orderIds: list[str] | None = None,
        cliOrdIds: list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures order status for specific order IDs."""
        payload: dict[str, Any] = {"orderIds": orderIds, "cliOrdIds": cliOrdIds}
        return await self._request(
            "POST",
            FuturesTrade.ORDER_STATUS,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    async def cancel_futures_order(
        self,
        order_id: str | None = None,
        cliOrdId: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken Futures order."""
        if order_id is None and cliOrdId is None:
            raise ValueError("Specify order_id or cliOrdId.")
        payload: dict[str, Any] = {"order_id": order_id, "cliOrdId": cliOrdId}
        return await self._request(
            "POST",
            FuturesTrade.CANCEL_ORDER,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    async def cancel_futures_all_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all Kraken Futures open orders, optionally filtered by product."""
        payload: dict[str, Any] = {}
        if product_symbol:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol)
        return await self._request(
            "POST",
            FuturesTrade.CANCEL_ALL,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )
