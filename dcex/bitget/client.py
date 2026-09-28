"""Bitget sync client module."""

from dataclasses import dataclass

from ._account_http import AccountHTTP
from ._earn_http import EarnHTTP
from ._generated import GeneratedHTTP
from ._trade_http import TradeHTTP


@dataclass
class Client(GeneratedHTTP, AccountHTTP, EarnHTTP, TradeHTTP):
    """Bitget sync client."""
