"""BingX swap account endpoints."""

from enum import Enum


class SwapAccount(str, Enum):
    """BingX swap account API endpoints."""

    ACCOUNT_BALANCE = "/openApi/swap/v3/user/balance"
    OPEN_POSITIONS = "/openApi/swap/v2/user/positions"
    FUND_FLOW = "/openApi/swap/v2/user/income"
    LISTEN_KEY = "/openApi/user/auth/userDataStream"

    def __str__(self) -> str:
        return self.value


class SpotAccount(str, Enum):
    """BingX spot account API endpoints."""

    ACCOUNT_BALANCE = "/openApi/spot/v1/account/balance"

    def __str__(self) -> str:
        return self.value


class FundAccount(str, Enum):
    """BingX fund account API endpoints."""

    ACCOUNT_BALANCE = "/openApi/fund/v1/account/balance"
    ALL_ACCOUNT_BALANCE = "/openApi/account/v1/allAccountBalance"
    ACCOUNT_UID = "/openApi/account/v1/uid"
    API_KEY_INFO = "/openApi/account/v1/apiKey/query"

    def __str__(self) -> str:
        return self.value


class TransferAccount(str, Enum):
    """BingX account transfer API endpoints."""

    TRANSFERABLE_COINS = "/openApi/api/asset/v1/transfer/supportCoins"
    ASSET_TRANSFER = "/openApi/api/asset/v1/transfer"
    TRANSFER_RECORDS = "/openApi/api/v3/asset/transferRecord"

    def __str__(self) -> str:
        return self.value
