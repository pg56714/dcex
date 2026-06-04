"""BitMart account API endpoints."""

from enum import Enum


class FundingAccount(str, Enum):
    """Funding account API endpoints for BitMart."""

    # https://api-cloud.bitmart.com
    GET_ACCOUNT_BALANCE = "/account/v1/wallet"
    GET_ACCOUNT_CURRENCIES = "/account/v1/currencies"
    GET_SPOT_WALLET_BALANCE = "/spot/v1/wallet"
    DEPOSIT_ADDRESS = "/account/v1/deposit/address"

    def __str__(self) -> str:
        return self.value


class FuturesAccount(str, Enum):
    """Futures account API endpoints for BitMart."""

    # https://api-cloud-v2.bitmart.com
    GET_CONTRACT_ASSETS = "/contract/private/assets-detail"

    def __str__(self) -> str:
        return self.value
