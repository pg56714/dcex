"""Bitget sync client module."""

from dataclasses import dataclass

from ._account_http import AccountHTTP
from ._earn_http import EarnHTTP
from ._inventory_http import InventoryHTTP
from ._trade_http import TradeHTTP


@dataclass
class Client(InventoryHTTP, AccountHTTP, EarnHTTP, TradeHTTP):
    """Bitget sync client."""
