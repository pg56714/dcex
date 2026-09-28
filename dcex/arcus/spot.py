"""Arcus public client composition."""

from dataclasses import dataclass

from ._account_http import SpotAccountHTTP
from ._market_http import SpotMarketHTTP
from ._trade_http import SpotTradeHTTP


@dataclass
class SpotClient(SpotMarketHTTP, SpotTradeHTTP, SpotAccountHTTP):
    "Arcus spot RFQ router; independent of the perpetuals client."
