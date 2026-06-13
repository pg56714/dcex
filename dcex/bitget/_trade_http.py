"""Bitget private trade HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade, UtaTrade


class TradeHTTP(HTTPManager):
    """HTTP client for Bitget private trading operations."""

    def _uta_symbol(
        self,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> str | None:
        if symbol is not None:
            return symbol
        if product_symbol is not None:
            return self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
        return None

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: str,
        price: str | None = None,
        force: str | None = None,
        clientOid: str | None = None,
        tpslType: str | None = None,
        stpMode: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot order."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "side": side,
            "orderType": orderType,
            "size": size,
            "price": price,
            "force": force,
            "clientOid": clientOid,
            "tpslType": tpslType,
            "stpMode": stpMode,
        }
        return self._request("POST", SpotTrade.PLACE_ORDER, payload, signed=True)

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market order."""
        return self.place_spot_order(product_symbol, side, "market", size, clientOid=clientOid)

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market buy order."""
        return self.place_spot_market_order(product_symbol, "buy", size, clientOid)

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market sell order."""
        return self.place_spot_market_order(product_symbol, "sell", size, clientOid)

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit order."""
        return self.place_spot_order(product_symbol, side, "limit", size, price, force, clientOid)

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit buy order."""
        return self.place_spot_limit_order(product_symbol, "buy", size, price, "gtc", clientOid)

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit sell order."""
        return self.place_spot_limit_order(product_symbol, "sell", size, price, "gtc", clientOid)

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit order."""
        return self.place_spot_limit_order(
            product_symbol, side, size, price, "post_only", clientOid
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit buy order."""
        return self.place_spot_post_only_limit_order(product_symbol, "buy", size, price, clientOid)

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit sell order."""
        return self.place_spot_post_only_limit_order(product_symbol, "sell", size, price, clientOid)

    def place_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Place Bitget spot orders in batch."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "batchMode": batchMode,
            "orderList": orderList,
        }
        return self._request("POST", SpotTrade.BATCH_PLACE_ORDER, payload, signed=True)

    def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        tpslType: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget spot order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "orderId": orderId,
            "clientOid": clientOid,
            "tpslType": tpslType,
        }
        return self._request("POST", SpotTrade.CANCEL_ORDER, payload, signed=True)

    def cancel_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Cancel Bitget spot orders in batch."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "batchMode": batchMode,
            "orderList": orderList,
        }
        return self._request("POST", SpotTrade.BATCH_CANCEL_ORDER, payload, signed=True)

    def get_spot_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget spot order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {"orderId": orderId, "clientOid": clientOid}
        return self._request("GET", SpotTrade.ORDER_INFO, payload, signed=True)

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot open orders."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "limit": limit,
            "idLessThan": idLessThan,
            "startTime": startTime,
            "endTime": endTime,
        }
        return self._request("GET", SpotTrade.UNFILLED_ORDERS, payload, signed=True)

    def get_spot_history_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot historical orders."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "limit": limit,
            "idLessThan": idLessThan,
            "startTime": startTime,
            "endTime": endTime,
        }
        return self._request("GET", SpotTrade.HISTORY_ORDERS, payload, signed=True)

    def get_spot_fills(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot fills."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "orderId": orderId,
            "limit": limit,
            "idLessThan": idLessThan,
            "startTime": startTime,
            "endTime": endTime,
        }
        return self._request("GET", SpotTrade.FILLS, payload, signed=True)

    def place_uta_order(
        self,
        category: str,
        product_symbol: str,
        side: str,
        orderType: str,
        qty: str,
        price: str | None = None,
        timeInForce: str | None = None,
        posSide: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
        stpMode: str | None = None,
        marginMode: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget UTA order."""
        payload: dict[str, Any] = {
            "category": category,
            "symbol": self._uta_symbol(product_symbol),
            "side": side,
            "orderType": orderType,
            "qty": qty,
            "price": price,
            "timeInForce": timeInForce,
            "posSide": posSide,
            "clientOid": clientOid,
            "reduceOnly": reduceOnly,
            "stpMode": stpMode,
            "marginMode": marginMode,
        }
        return self._request("POST", UtaTrade.PLACE_ORDER, payload, signed=True)

    def place_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Place Bitget UTA orders in batch."""
        return self._request("POST", UtaTrade.BATCH_PLACE_ORDER, orderList, signed=True)

    def cancel_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {
            "orderId": orderId,
            "clientOid": clientOid,
            "category": category,
        }
        return self._request("POST", UtaTrade.CANCEL_ORDER, payload, signed=True)

    def cancel_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel Bitget UTA orders in batch."""
        return self._request("POST", UtaTrade.BATCH_CANCEL_ORDERS, orderList, signed=True)

    def get_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget UTA order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {"orderId": orderId, "clientOid": clientOid}
        return self._request("GET", UtaTrade.ORDER_DETAIL, payload, signed=True)

    def get_uta_open_orders(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        symbol: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA open orders."""
        payload: dict[str, Any] = {
            "category": category,
            "symbol": self._uta_symbol(product_symbol, symbol),
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "cursor": cursor,
        }
        return self._request("GET", UtaTrade.PENDING_ORDERS, payload, signed=True)

    def get_uta_history_orders(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA historical orders."""
        payload: dict[str, Any] = {
            "category": category,
            "symbol": self._uta_symbol(product_symbol, symbol),
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "cursor": cursor,
        }
        return self._request("GET", UtaTrade.HISTORY_ORDERS, payload, signed=True)

    def get_uta_fills(
        self,
        category: str | None = None,
        orderId: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA fills."""
        payload: dict[str, Any] = {
            "category": category,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "cursor": cursor,
        }
        return self._request("GET", UtaTrade.FILLS, payload, signed=True)

    def get_uta_positions(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        posSide: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA positions."""
        payload: dict[str, Any] = {
            "category": category,
            "symbol": self._uta_symbol(product_symbol, symbol),
            "posSide": posSide,
        }
        return self._request("GET", UtaTrade.POSITIONS, payload, signed=True)

    def place_futures_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: str,
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        price: str | None = None,
        tradeSide: str | None = None,
        force: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures order."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "size": size,
            "price": price,
            "side": side,
            "tradeSide": tradeSide,
            "orderType": orderType,
            "force": force,
            "clientOid": clientOid,
            "reduceOnly": reduceOnly,
        }
        return self._request("POST", FuturesTrade.PLACE_ORDER, payload, signed=True)

    def place_futures_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        tradeSide: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures market order."""
        return self.place_futures_order(
            product_symbol,
            side,
            "market",
            size,
            marginMode,
            marginCoin,
            productType,
            tradeSide=tradeSide,
            clientOid=clientOid,
            reduceOnly=reduceOnly,
        )

    def place_futures_market_buy_order(self, product_symbol: str, size: str) -> dict[str, Any]:
        """Place a Bitget futures market buy order."""
        return self.place_futures_market_order(product_symbol, "buy", size)

    def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures market sell order."""
        return self.place_futures_market_order(product_symbol, "sell", size, reduceOnly=reduceOnly)

    def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit order."""
        return self.place_futures_order(
            product_symbol,
            side,
            "limit",
            size,
            price=price,
            force=force,
            clientOid=clientOid,
        )

    def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit buy order."""
        return self.place_futures_limit_order(product_symbol, "buy", size, price, "gtc", clientOid)

    def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit sell order."""
        return self.place_futures_limit_order(product_symbol, "sell", size, price, "gtc", clientOid)

    def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit order."""
        return self.place_futures_limit_order(
            product_symbol,
            side,
            size,
            price,
            "post_only",
            clientOid,
        )

    def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit buy order."""
        return self.place_futures_post_only_limit_order(
            product_symbol, "buy", size, price, clientOid
        )

    def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit sell order."""
        return self.place_futures_post_only_limit_order(
            product_symbol, "sell", size, price, clientOid
        )

    def place_futures_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Place Bitget futures orders in batch."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "orderList": orderList,
        }
        return self._request("POST", FuturesTrade.BATCH_PLACE_ORDER, payload, signed=True)

    def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel a Bitget futures order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
            "orderId": orderId,
            "clientOid": clientOid,
        }
        return self._request("POST", FuturesTrade.CANCEL_ORDER, payload, signed=True)

    def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[dict[str, Any]] | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel Bitget futures orders in batch."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "marginCoin": marginCoin,
            "orderIdList": orderIdList,
        }
        return self._request("POST", FuturesTrade.BATCH_CANCEL_ORDERS, payload, signed=True)

    def get_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures order."""
        if orderId is None and clientOid is None:
            raise ValueError("Specify orderId or clientOid.")
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "orderId": orderId,
            "clientOid": clientOid,
        }
        return self._request("GET", FuturesTrade.ORDER_DETAIL, payload, signed=True)

    def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        orderId: str | None = None,
        clientOid: str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open orders."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "productType": productType,
            "orderId": orderId,
            "clientOid": clientOid,
            "idLessThan": idLessThan,
            "limit": limit,
        }
        return self._request("GET", FuturesTrade.PENDING_ORDERS, payload, signed=True)

    def get_futures_history_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures historical orders."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "productType": productType,
            "startTime": startTime,
            "endTime": endTime,
            "idLessThan": idLessThan,
            "limit": limit,
        }
        return self._request("GET", FuturesTrade.HISTORY_ORDERS, payload, signed=True)

    def get_futures_fills(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        productType: str = "USDT-FUTURES",
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures fills."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {
            "symbol": symbol,
            "orderId": orderId,
            "productType": productType,
            "idLessThan": idLessThan,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
        }
        return self._request("GET", FuturesTrade.FILLS, payload, signed=True)
