"""MEXC async private trading HTTP client."""

import json
from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import ContractTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """Async HTTP client for MEXC private trading APIs."""

    def _spot_symbol(self, product_symbol: str) -> str:
        return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)

    def _contract_symbol(self, product_symbol: str) -> str:
        return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)

    async def test_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Validate a MEXC Spot order without placing it."""
        payload = {
            "symbol": self._spot_symbol(product_symbol),
            "side": side,
            "type": type_,
            "quantity": quantity,
            "quoteOrderQty": quoteOrderQty,
            "price": price,
            "timeInForce": timeInForce,
            "newClientOrderId": newClientOrderId,
            "recvWindow": recvWindow,
        }
        return await self._request("POST", SpotTrade.TEST_ORDER, payload)

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot order."""
        payload = {
            "symbol": self._spot_symbol(product_symbol),
            "side": side,
            "type": type_,
            "quantity": quantity,
            "quoteOrderQty": quoteOrderQty,
            "price": price,
            "timeInForce": timeInForce,
            "newClientOrderId": newClientOrderId,
            "recvWindow": recvWindow,
        }
        return await self._request("POST", SpotTrade.ORDER, payload)

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit order."""
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit buy order."""
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit sell order."""
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit order."""
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT_MAKER",
            quantity=quantity,
            price=price,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit buy order."""
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit sell order."""
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market order."""
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type_="MARKET",
            quantity=quantity,
            quoteOrderQty=quoteOrderQty,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        quoteOrderQty: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market buy order by quote quantity."""
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="BUY",
            quoteOrderQty=quoteOrderQty,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market sell order by base quantity."""
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            newClientOrderId=newClientOrderId,
            recvWindow=recvWindow,
        )

    async def place_spot_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place MEXC Spot batch orders."""
        normalized_orders = []
        for order in batchOrders:
            normalized = dict(order)
            if "product_symbol" in normalized:
                normalized["symbol"] = self._spot_symbol(str(normalized.pop("product_symbol")))
            normalized_orders.append(normalized)
        return await self._request(
            "POST",
            SpotTrade.BATCH_ORDERS,
            {
                "batchOrders": json.dumps(normalized_orders, separators=(",", ":")),
                "recvWindow": recvWindow,
            },
        )

    async def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Spot order."""
        return await self._request(
            "DELETE",
            SpotTrade.ORDER,
            {
                "symbol": self._spot_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    async def cancel_spot_open_orders(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Spot open orders for a symbol."""
        return await self._request(
            "DELETE",
            SpotTrade.OPEN_ORDERS,
            {"symbol": self._spot_symbol(product_symbol), "recvWindow": recvWindow},
        )

    async def get_spot_order(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Spot order."""
        return await self._request(
            "GET",
            SpotTrade.ORDER,
            {
                "symbol": self._spot_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot open orders."""
        return await self._request(
            "GET",
            SpotTrade.OPEN_ORDERS,
            {"symbol": self._spot_symbol(product_symbol), "recvWindow": recvWindow},
        )

    async def get_spot_all_orders(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Spot orders for a symbol."""
        return await self._request(
            "GET",
            SpotTrade.ALL_ORDERS,
            {
                "symbol": self._spot_symbol(product_symbol),
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    async def get_spot_my_trades(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account trade fills."""
        return await self._request(
            "GET",
            SpotTrade.MY_TRADES,
            {
                "symbol": self._spot_symbol(product_symbol),
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    async def place_contract_order(
        self,
        product_symbol: str,
        side: int,
        type_: int,
        openType: int,
        vol: int | str,
        price: str | None = None,
        leverage: int | None = None,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
        stopLossPrice: str | None = None,
        takeProfitPrice: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract order."""
        return await self._request(
            "POST",
            ContractTrade.CREATE_ORDER,
            {
                "symbol": self._contract_symbol(product_symbol),
                "side": side,
                "type": type_,
                "openType": openType,
                "vol": vol,
                "price": price,
                "leverage": leverage,
                "externalOid": externalOid,
                "positionMode": positionMode,
                "reduceOnly": reduceOnly,
                "stopLossPrice": stopLossPrice,
                "takeProfitPrice": takeProfitPrice,
            },
            api="contract",
        )

    async def place_contract_limit_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit order."""
        return await self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type_=1,
            openType=openType,
            vol=vol,
            price=price,
            leverage=leverage,
            externalOid=externalOid,
            positionMode=positionMode,
            reduceOnly=reduceOnly,
        )

    async def place_contract_limit_buy_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit buy order."""
        return await self.place_contract_limit_order(
            product_symbol=product_symbol,
            side=1,
            price=price,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def place_contract_limit_sell_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit sell order."""
        return await self.place_contract_limit_order(
            product_symbol=product_symbol,
            side=3,
            price=price,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def place_contract_post_only_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only order."""
        return await self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type_=2,
            openType=openType,
            vol=vol,
            price=price,
            leverage=leverage,
            externalOid=externalOid,
            positionMode=positionMode,
            reduceOnly=reduceOnly,
        )

    async def place_contract_post_only_buy_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only buy order."""
        return await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=1,
            price=price,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def place_contract_post_only_sell_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only sell order."""
        return await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=3,
            price=price,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def place_contract_market_order(
        self,
        product_symbol: str,
        side: int,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market order."""
        return await self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type_=5,
            openType=openType,
            vol=vol,
            leverage=leverage,
            externalOid=externalOid,
            positionMode=positionMode,
            reduceOnly=reduceOnly,
        )

    async def place_contract_market_buy_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market buy order."""
        return await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=1,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def place_contract_market_sell_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market sell order."""
        return await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=3,
            vol=vol,
            leverage=leverage,
            openType=openType,
            externalOid=externalOid,
            positionMode=positionMode,
        )

    async def cancel_contract_orders(
        self,
        orders: list[str | int | dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Cancel MEXC Contract orders by order id list."""
        order_ids = [order.get("orderId") if isinstance(order, dict) else order for order in orders]
        return await self._request("POST", ContractTrade.CANCEL_ORDERS, order_ids, api="contract")

    async def cancel_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by order id."""
        return await self.cancel_contract_orders([order_id])

    async def cancel_contract_order_with_external_id(
        self,
        product_symbol: str,
        externalOid: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by external order id."""
        return await self._request(
            "POST",
            ContractTrade.CANCEL_ORDER_WITH_EXTERNAL_ID,
            {"symbol": self._contract_symbol(product_symbol), "externalOid": externalOid},
            api="contract",
        )

    async def cancel_all_contract_orders(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Contract orders for a symbol."""
        return await self._request(
            "POST",
            ContractTrade.CANCEL_ALL_ORDERS,
            {"symbol": self._contract_symbol(product_symbol)},
            api="contract",
        )

    async def get_contract_open_orders(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract open orders."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractTrade.OPEN_ORDERS).format(symbol=symbol)
        return await self._request(
            "GET",
            path,
            {"page_num": page_num, "page_size": page_size},
            api="contract",
        )

    async def get_contract_history_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        category: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical orders."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractTrade.HISTORY_ORDERS,
            {
                "symbol": symbol,
                "states": states,
                "category": category,
                "start_time": start_time,
                "end_time": end_time,
                "page_num": page_num,
                "page_size": page_size,
            },
            api="contract",
        )

    async def get_contract_order_by_external_id(
        self,
        product_symbol: str,
        external_oid: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by external order id."""
        path = str(ContractTrade.EXTERNAL_ORDER).format(
            symbol=self._contract_symbol(product_symbol),
            external_oid=external_oid,
        )
        return await self._request("GET", path, api="contract")

    async def get_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by order id."""
        path = str(ContractTrade.ORDER).format(order_id=order_id)
        return await self._request("GET", path, api="contract")

    async def get_contract_orders(
        self,
        order_ids: list[str | int] | str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orders by order ids."""
        joined_order_ids = (
            ",".join(map(str, order_ids)) if isinstance(order_ids, list) else order_ids
        )
        return await self._request(
            "GET",
            ContractTrade.BATCH_QUERY,
            {"order_ids": joined_order_ids},
            api="contract",
        )

    async def get_contract_order_deal_details(
        self,
        order_id: str | int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deal details."""
        path = str(ContractTrade.ORDER_DEAL_DETAILS).format(order_id=order_id)
        return await self._request("GET", path, api="contract")

    async def get_contract_order_deals(
        self,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deals."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractTrade.ORDER_DEALS,
            {
                "symbol": symbol,
                "start_time": start_time,
                "end_time": end_time,
                "page_num": page_num,
                "page_size": page_size,
            },
            api="contract",
        )

    async def get_contract_plan_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trigger orders."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractTrade.PLAN_ORDERS,
            {"symbol": symbol, "states": states, "page_num": page_num, "page_size": page_size},
            api="contract",
        )

    async def get_contract_stop_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract Stop-Limit orders."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractTrade.STOP_ORDERS,
            {"symbol": symbol, "states": states, "page_num": page_num, "page_size": page_size},
            api="contract",
        )
