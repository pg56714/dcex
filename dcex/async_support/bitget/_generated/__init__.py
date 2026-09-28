"""Compose generated domain methods with the handwritten client bases."""

from .._market_http import MarketHTTP
from .announcements_http import GeneratedAnnouncementsHTTP
from .broker_http import GeneratedBrokerHTTP
from .cfd_http import GeneratedCfdHTTP
from .convert_http import GeneratedConvertHTTP
from .copy_trading_http import GeneratedCopyTradingHTTP
from .earn_http import GeneratedEarnHTTP
from .institutional_loan_http import GeneratedInstitutionalLoanHTTP
from .loan_http import GeneratedLoanHTTP
from .margin_http import GeneratedMarginHTTP
from .market_http import GeneratedMarketHTTP
from .p2p_http import GeneratedP2pHTTP
from .stocks_http import GeneratedStocksHTTP
from .tax_http import GeneratedTaxHTTP
from .transfers_http import GeneratedTransfersHTTP
from .withdrawals_http import GeneratedWithdrawalsHTTP


class GeneratedHTTP(
    GeneratedAnnouncementsHTTP,
    GeneratedBrokerHTTP,
    GeneratedCfdHTTP,
    GeneratedConvertHTTP,
    GeneratedCopyTradingHTTP,
    GeneratedEarnHTTP,
    GeneratedInstitutionalLoanHTTP,
    GeneratedLoanHTTP,
    GeneratedMarginHTTP,
    GeneratedMarketHTTP,
    GeneratedP2pHTTP,
    GeneratedStocksHTTP,
    GeneratedTaxHTTP,
    GeneratedTransfersHTTP,
    GeneratedWithdrawalsHTTP,
    MarketHTTP,
):
    """Business-specific generated methods with compatible base precedence."""

    close_copy_futures_follower_positions = vars(GeneratedCopyTradingHTTP)[
        "classic_copytrading_future_copytrade_follower_close_positions"
    ]
    close_copy_futures_trader_positions = vars(GeneratedCopyTradingHTTP)[
        "classic_copytrading_future_copytrade_trader_trader_order_close_positions"
    ]
