"""Binance COIN-M API methods backed by Rust."""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP


class CoinFuturesHTTP(AccountHTTP, MarketHTTP):
    """COIN-M endpoints use native symbols such as BTCUSD_PERP."""

    def get_coin_futures_exchange_info(self) -> dict[str, Any]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public("get_coin_futures_exchange_info", self._params())

    def get_coin_futures_orderbook(self, symbol: str, limit: int | None = None) -> dict[str, Any]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_orderbook", self._params(symbol=symbol, limit=limit)
        )

    def get_coin_futures_trades(
        self, symbol: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_trades", self._params(symbol=symbol, limit=limit)
        )

    def get_coin_futures_klines(
        self,
        symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_klines",
            self._params(
                symbol=symbol, interval=interval, startTime=startTime, endTime=endTime, limit=limit
            ),
        )

    def get_coin_futures_ticker(
        self, symbol: str | None = None, pair: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_ticker", self._params(symbol=symbol, pair=pair)
        )

    def get_coin_futures_mark_price(
        self, symbol: str | None = None, pair: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_mark_price", self._params(symbol=symbol, pair=pair)
        )

    def get_coin_futures_funding_rate(
        self,
        symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Call the Binance COIN-M public endpoint."""
        return self._native_public(
            "get_coin_futures_funding_rate",
            self._params(symbol=symbol, startTime=startTime, endTime=endTime, limit=limit),
        )

    def get_coin_futures_balance(self) -> list[dict[str, Any]]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private("get_coin_futures_balance", self._params())

    def get_coin_futures_account(self) -> dict[str, Any]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private("get_coin_futures_account", self._params())

    def get_coin_futures_positions(
        self, marginAsset: str | None = None, pair: str | None = None
    ) -> list[dict[str, Any]]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private(
            "get_coin_futures_positions", self._params(marginAsset=marginAsset, pair=pair)
        )

    def get_coin_futures_open_orders(
        self, symbol: str | None = None, pair: str | None = None
    ) -> list[dict[str, Any]]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private(
            "get_coin_futures_open_orders", self._params(symbol=symbol, pair=pair)
        )

    def get_coin_futures_order(
        self, symbol: str, orderId: int | None = None, origClientOrderId: str | None = None
    ) -> dict[str, Any]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private(
            "get_coin_futures_order",
            self._params(symbol=symbol, orderId=orderId, origClientOrderId=origClientOrderId),
        )

    def place_coin_futures_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
        timeInForce: str | None = None,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
        newClientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private(
            "place_coin_futures_order",
            self._params(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newClientOrderId=newClientOrderId,
            ),
        )

    def cancel_coin_futures_order(
        self, symbol: str, orderId: int | None = None, origClientOrderId: str | None = None
    ) -> dict[str, Any]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private(
            "cancel_coin_futures_order",
            self._params(symbol=symbol, orderId=orderId, origClientOrderId=origClientOrderId),
        )

    def cancel_all_coin_futures_orders(self, symbol: str) -> dict[str, Any]:
        """Call the Binance COIN-M private endpoint."""
        return self._native_private("cancel_all_coin_futures_orders", self._params(symbol=symbol))
