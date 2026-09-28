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
    MarketHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
