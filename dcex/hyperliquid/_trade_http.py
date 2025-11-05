"""Trading-related HTTP API client for Hyperliquid exchange."""

from typing import Any

import msgspec

from ..utils.common import Common
from ._http_manager import HTTPManager
from ._market_http import MarketHTTP
from .endpoint.path import Path
from .endpoint.trade import Trade


class TradeHTTP(HTTPManager):
    """HTTP client for trading operations on Hyperliquid exchange."""

    def place_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place an order on the exchange.

        Args:
            product_symbol: Product symbol
            isBuy: Whether this is a buy order
            price: Order price
            size: Order size
            reduceOnly: Whether this is a reduce-only order
            tif: Time in force
            isMarket: Whether this is a market order
            triggerPx: Trigger price for conditional orders
            tpsl: Take profit/stop loss
            cloid: Client order ID
            grouping: Order grouping
            builder_address: Builder address
            fee_ten_bp: Fee in basis points
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing order placement result
        """
        action = {
            "type": Trade.ORDER,
            "orders": [
                {
                    "a": msgspec.json.decode(
                        self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
                    )[1],
                    "b": isBuy,
                    "p": price,
                    "s": size,
                    "r": reduceOnly,
                }
            ],
            "grouping": grouping,
        }

        if tif is not None or isMarket:
            t = {}
            if tif is not None:
                t["limit"] = {"tif": tif}
            else:
                t["trigger"] = {
                    "isMarket": isMarket,
                    "triggerPx": triggerPx,
                    "tpsl": tpsl,
                }
            action["orders"][0]["t"] = t

        if cloid is not None:
            action["orders"][0]["c"] = cloid
        if builder_address is not None:
            action["builder"]["b"] = builder_address
        if fee_ten_bp is not None:
            action["feeTenBp"] = fee_ten_bp

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }

        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def place_future_market_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a future market order.

        Args:
            product_symbol: Product symbol
            isBuy: Whether this is a buy order
            size: Order size
            triggerPx: Trigger price for conditional orders
            tpsl: Take profit/stop loss

        Returns:
            Dict containing order placement result
        """
        market_http = MarketHTTP()
        result: Any = market_http.get_meta_and_asset_ctxs()
        exchange_symbol = msgspec.json.decode(
            self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
        )[1]
        asset_contexts = result[1]
        price = asset_contexts[exchange_symbol]["midPx"]

        return self.place_order(
            product_symbol=product_symbol,
            isBuy=isBuy,
            price=price.split(".", 1)[0],
            size=size,
            reduceOnly=False,
            isMarket=True,
            triggerPx=triggerPx,
            tpsl=tpsl,
            vaultAddress=vaultAddress,
            expireAfter=expireAfter,
        )

    def place_future_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a future market buy order.

        Args:
            product_symbol: Product symbol
            size: Order size
            triggerPx: Trigger price for conditional orders
            tpsl: Take profit/stop loss

        Returns:
            Dict containing order placement result
        """
        return self.place_future_market_order(
            product_symbol=product_symbol,
            isBuy=True,
            size=size,
            triggerPx=triggerPx,
            tpsl=tpsl,
            vaultAddress=vaultAddress,
            expireAfter=expireAfter,
        )

    def place_future_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a future market sell order.

        Args:
            product_symbol: Product symbol
            size: Order size
            triggerPx: Trigger price for conditional orders
            tpsl: Take profit/stop loss

        Returns:
            Dict containing order placement result
        """
        return self.place_future_market_order(
            product_symbol=product_symbol,
            isBuy=False,
            size=size,
            triggerPx=triggerPx,
            tpsl=tpsl,
            vaultAddress=vaultAddress,
            expireAfter=expireAfter,
        )

    def place_future_limit_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """
        Place a future limit order.

        Args:
            product_symbol: Product symbol
            isBuy: Whether this is a buy order
            price: Order price
            size: Order size
            tif: Time in force

        Returns:
            Dict containing order placement result
        """
        return self.place_order(
            product_symbol=product_symbol,
            isBuy=isBuy,
            price=price,
            size=size,
            reduceOnly=False,
            tif=tif,
        )

    def place_future_limit_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """
        Place a future limit buy order.

        Args:
            product_symbol: Product symbol
            price: Order price
            size: Order size
            tif: Time in force

        Returns:
            Dict containing order placement result
        """
        return self.place_order(
            product_symbol=product_symbol,
            isBuy=True,
            price=price,
            size=size,
            reduceOnly=False,
            tif=tif,
        )

    def place_future_limit_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """
        Place a future limit sell order.

        Args:
            product_symbol: Product symbol
            price: Order price
            size: Order size
            tif: Time in force

        Returns:
            Dict containing order placement result
        """
        return self.place_order(
            product_symbol=product_symbol,
            isBuy=False,
            price=price,
            size=size,
            reduceOnly=False,
            tif=tif,
        )

    def cancel_order(
        self,
        product_symbol: str,
        oid: int,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an order by order ID.

        Args:
            product_symbol: Product symbol
            oid: Order ID
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing cancellation result
        """
        action = {
            "type": Trade.CANCEL,
            "cancels": [
                {
                    "a": msgspec.json.decode(
                        self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
                    )[1],
                    "o": oid,
                }
            ],
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }
        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def cancel_order_by_cloid(
        self,
        product_symbol: str,
        cloid: str,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an order by client order ID.

        Args:
            product_symbol: Product symbol
            cloid: Client order ID
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing cancellation result
        """
        action = {
            "type": Trade.CANCELBYCLOID,
            "cancels": [
                {
                    "asset": msgspec.json.decode(
                        self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
                    )[1],
                    "cloid": cloid,
                }
            ],
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }
        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def schedule_cancel(
        self,
        time: int | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Schedule order cancellation.

        Args:
            time: Cancellation time
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing scheduling result
        """
        action = {
            "type": Trade.SCHEDULECANCEL,
            "time": time,
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }
        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def modify_order(
        self,
        oid: int,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Modify an existing order.

        Args:
            oid: Order ID to modify
            product_symbol: Product symbol
            isBuy: Whether this is a buy order
            price: Order price
            size: Order size
            reduceOnly: Whether this is a reduce-only order
            tif: Time in force
            isMarket: Whether this is a market order
            triggerPx: Trigger price for conditional orders
            tpsl: Take profit/stop loss
            cloid: Client order ID
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing modification result
        """
        action = {
            "type": Trade.MODIFY,
            "oid": oid,
            "order": {
                "a": msgspec.json.decode(
                    self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
                )[1],
                "b": isBuy,
                "p": price,
                "s": size,
                "r": reduceOnly,
            },
        }

        if tif is not None or isMarket:
            t = {}
            if tif is not None:
                t["limit"] = {"tif": tif}
            else:
                t["trigger"] = {
                    "isMarket": isMarket,
                    "triggerPx": triggerPx,
                    "tpsl": tpsl,
                }
            action["order"]["t"] = t
        if cloid is not None:
            action["order"]["c"] = cloid

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }

        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def modify_batch_orders(
        self, modifies: list, vaultAddress: str | None = None, expireAfter: int | None = None
    ) -> dict[str, Any]:
        """
        Modify multiple orders in batch.

        Args:
            modifies: List of order modifications
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing batch modification result
        """
        action = {"type": Trade.BATCHMODIFY, "modifies": modifies}

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }

        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def update_leverage(
        self,
        product_symbol: str,
        isCross: bool,
        leverage: int,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Update leverage for a product.

        Args:
            product_symbol: Product symbol
            isCross: Whether to use cross margin
            leverage: Leverage value
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing leverage update result
        """
        action = {
            "type": Trade.UPDATELEVERAGE,
            "asset": msgspec.json.decode(
                self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
            )[1],
            "isCross": isCross,
            "leverage": leverage,
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }
        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def update_isolate_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Update isolated margin for a product.

        Args:
            product_symbol: Product symbol
            isBuy: Whether this is a buy position
            ntli: Net total long interest
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing margin update result
        """
        action = {
            "type": Trade.UPDATEISOLATEMARGIN,
            "asset": msgspec.json.decode(
                self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
            )[1],
            "isBuy": isBuy,
            "ntli": ntli,
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }
        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def place_twap_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        reduceOnly: bool,
        minutes: int,
        randomize: bool,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a TWAP (Time-Weighted Average Price) order.

        Args:
            product_symbol: Product symbol
            isBuy: Whether this is a buy order
            size: Order size
            reduceOnly: Whether this is a reduce-only order
            minutes: Duration in minutes
            randomize: Whether to randomize execution
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing TWAP order placement result
        """
        action = {
            "type": Trade.TWAPORDER,
            "twap": {
                "a": msgspec.json.decode(
                    self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
                )[1],
                "b": isBuy,
                "s": size,
                "r": reduceOnly,
                "m": minutes,
                "t": randomize,
            },
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }

        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res

    def cancel_twap_order(
        self,
        product_symbol: str,
        twap_id: int,
        vaultAddress: str | None = None,
        expireAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a TWAP order.

        Args:
            product_symbol: Product symbol
            twap_id: TWAP order ID
            vaultAddress: Vault address
            expireAfter: Expiration timestamp

        Returns:
            Dict containing TWAP cancellation result
        """
        action = {
            "type": Trade.TWAPCANCEL,
            "a": msgspec.json.decode(
                self._get_ptm().get_exchange_symbol(Common.HYPERLIQUID, product_symbol)
            )[1],
            "t": twap_id,
        }

        payload = {
            "action": action,
            "nonce": "",
            "signature": "",
        }

        if vaultAddress is not None:
            payload["vaultAddress"] = vaultAddress
        if expireAfter is not None:
            payload["expireAfter"] = expireAfter

        res = self._request(
            method="POST",
            path=Path.EXCHANGE,
            query=payload,
            signed=True,
        )
        return res
