"""Ondo asynchronous client."""

from dataclasses import dataclass

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._spot_http import SpotTradeHTTP
from ._trade_http import TradeHTTP


@dataclass
class Client(MarketHTTP, AccountHTTP, TradeHTTP, SpotTradeHTTP):
    """Combined async Ondo REST client."""
