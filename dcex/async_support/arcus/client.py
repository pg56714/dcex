"""Arcus public client composition."""

from dataclasses import dataclass

from ._account_http import AccountHTTP
from ._batch_http import ClientBatchHTTP
from ._http_manager import _params as _params
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP
from ._transfers_http import ClientTransfersHTTP
from ._withdrawals_http import ClientWithdrawalsHTTP


@dataclass
class Client(
    MarketHTTP, TradeHTTP, AccountHTTP, ClientTransfersHTTP, ClientWithdrawalsHTTP, ClientBatchHTTP
):
    "Arcus perps; pass testnet=True to select the testnet endpoint."
