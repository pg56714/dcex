"""Extended sync client module."""

from dataclasses import dataclass

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


@dataclass
class Client(MarketHTTP, AccountHTTP, TradeHTTP):
    """Extended sync client."""
