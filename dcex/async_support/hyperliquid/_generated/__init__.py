"""Compose generated domain methods with the handwritten client bases."""

from .._trade_http import TradeHTTP
from .account_http import GeneratedAccountHTTP
from .administration_http import GeneratedAdministrationHTTP
from .deployment_http import GeneratedDeploymentHTTP
from .market_http import GeneratedMarketHTTP


class GeneratedHTTP(
    GeneratedAccountHTTP,
    GeneratedAdministrationHTTP,
    GeneratedDeploymentHTTP,
    GeneratedMarketHTTP,
    TradeHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
