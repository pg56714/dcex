"""Compose generated domain methods with the handwritten client bases."""

from .._market_http import MarketHTTP
from .account_http import GeneratedAccountHTTP
from .affiliate_http import GeneratedAffiliateHTTP
from .alpha_http import GeneratedAlphaHTTP
from .bots_http import GeneratedBotsHTTP
from .broker_http import GeneratedBrokerHTTP
from .card_http import GeneratedCardHTTP
from .compliance_http import GeneratedComplianceHTTP
from .convert_http import GeneratedConvertHTTP
from .event_http import GeneratedEventHTTP
from .fiat_http import GeneratedFiatHTTP
from .file_upload_http import GeneratedFileUploadHTTP
from .leveraged_tokens_http import GeneratedLeveragedTokensHTTP
from .loan_http import GeneratedLoanHTTP
from .pwm_http import GeneratedPwmHTTP
from .referral_http import GeneratedReferralHTTP
from .stocks_http import GeneratedStocksHTTP
from .subaccount_http import GeneratedSubaccountHTTP
from .trading_http import GeneratedTradingHTTP
from .withdrawals_http import GeneratedWithdrawalsHTTP


class GeneratedHTTP(
    GeneratedAccountHTTP,
    GeneratedAffiliateHTTP,
    GeneratedAlphaHTTP,
    GeneratedBotsHTTP,
    GeneratedBrokerHTTP,
    GeneratedCardHTTP,
    GeneratedComplianceHTTP,
    GeneratedConvertHTTP,
    GeneratedEventHTTP,
    GeneratedFiatHTTP,
    GeneratedFileUploadHTTP,
    GeneratedLeveragedTokensHTTP,
    GeneratedLoanHTTP,
    GeneratedPwmHTTP,
    GeneratedReferralHTTP,
    GeneratedStocksHTTP,
    GeneratedSubaccountHTTP,
    GeneratedTradingHTTP,
    GeneratedWithdrawalsHTTP,
    MarketHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
