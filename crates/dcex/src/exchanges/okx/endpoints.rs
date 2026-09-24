pub(super) const BASE_URL: &str = "https://openapi.okx.com";
pub(super) const PUBLIC_INSTRUMENTS: &str = "/api/v5/public/instruments";
pub(super) const PUBLIC_UNDERLYING: &str = "/api/v5/public/underlying";
pub(super) const PUBLIC_FUNDING_RATE: &str = "/api/v5/public/funding-rate";
pub(super) const PUBLIC_FUNDING_RATE_HISTORY: &str = "/api/v5/public/funding-rate-history";
pub(super) const PUBLIC_OPEN_INTEREST: &str = "/api/v5/public/open-interest";
pub(super) const PUBLIC_POSITION_TIERS: &str = "/api/v5/public/position-tiers";
pub(super) const PUBLIC_TRADING_DATA_SUPPORT_COIN: &str =
    "/api/v5/rubik/stat/trading-data/support-coin";
pub(super) const PUBLIC_TAKER_VOLUME: &str = "/api/v5/rubik/stat/taker-volume";
pub(super) const PUBLIC_CONTRACT_TAKER_VOLUME: &str = "/api/v5/rubik/stat/taker-volume-contract";
pub(super) const PUBLIC_LONG_SHORT_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-account-ratio";
pub(super) const PUBLIC_CONTRACT_LONG_SHORT_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract";
pub(super) const PUBLIC_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader";
pub(super) const PUBLIC_TOP_TRADER_LONG_SHORT_POSITION_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader";
pub(super) const PUBLIC_CONTRACTS_OPEN_INTEREST_VOLUME: &str =
    "/api/v5/rubik/stat/contracts/open-interest-volume";
pub(super) const PUBLIC_CONTRACT_OPEN_INTEREST_HISTORY: &str =
    "/api/v5/rubik/stat/contracts/open-interest-history";
pub(super) const PUBLIC_DELIVERY_EXERCISE_HISTORY: &str =
    "/api/v5/public/delivery-exercise-history";
pub(super) const PUBLIC_OPTION_SUMMARY: &str = "/api/v5/public/opt-summary";
pub(super) const PUBLIC_OPTION_TICK_BANDS: &str = "/api/v5/public/instrument-tick-bands";
pub(super) const PUBLIC_OPTION_TRADES: &str = "/api/v5/public/option-trades";
pub(super) const MARKET_OPTION_FAMILY_TRADES: &str =
    "/api/v5/market/option/instrument-family-trades";
pub(super) const PUBLIC_OPTIONS_OPEN_INTEREST_VOLUME: &str =
    "/api/v5/rubik/stat/option/open-interest-volume";
pub(super) const PUBLIC_OPTION_PUT_CALL_RATIO: &str =
    "/api/v5/rubik/stat/option/open-interest-volume-ratio";
pub(super) const PUBLIC_OPTION_OPEN_INTEREST_VOLUME_EXPIRY: &str =
    "/api/v5/rubik/stat/option/open-interest-volume-expiry";
pub(super) const PUBLIC_OPTION_OPEN_INTEREST_VOLUME_STRIKE: &str =
    "/api/v5/rubik/stat/option/open-interest-volume-strike";
pub(super) const PUBLIC_OPTION_TAKER_BLOCK_VOLUME: &str =
    "/api/v5/rubik/stat/option/taker-block-volume";
pub(super) const MARKET_CANDLES: &str = "/api/v5/market/candles";
pub(super) const MARKET_ORDERBOOK: &str = "/api/v5/market/books";
pub(super) const MARKET_TICKERS: &str = "/api/v5/market/tickers";
pub(super) const MARKET_PUBLIC_TRADES: &str = "/api/v5/market/trades";
pub(super) const ACCOUNT_INSTRUMENTS: &str = "/api/v5/account/instruments";
pub(super) const ACCOUNT_BALANCE: &str = "/api/v5/account/balance";
pub(super) const ACCOUNT_POSITIONS: &str = "/api/v5/account/positions";
pub(super) const ACCOUNT_POSITIONS_HISTORY: &str = "/api/v5/account/positions-history";
pub(super) const ACCOUNT_POSITION_RISK: &str = "/api/v5/account/account-position-risk";
pub(super) const ACCOUNT_BILLS: &str = "/api/v5/account/bills";
pub(super) const ACCOUNT_BILLS_ARCHIVE: &str = "/api/v5/account/bills-archive";
pub(super) const ACCOUNT_BILLS_HISTORY_ARCHIVE: &str = "/api/v5/account/bills-history-archive";
pub(super) const ACCOUNT_CONFIG: &str = "/api/v5/account/config";
pub(super) const ACCOUNT_SET_POSITION_MODE: &str = "/api/v5/account/set-position-mode";
pub(super) const ACCOUNT_SET_LEVERAGE: &str = "/api/v5/account/set-leverage";
pub(super) const ACCOUNT_MAX_SIZE: &str = "/api/v5/account/max-size";
pub(super) const ACCOUNT_MAX_AVAIL_SIZE: &str = "/api/v5/account/max-avail-size";
pub(super) const ACCOUNT_LEVERAGE_INFO: &str = "/api/v5/account/leverage-info";
pub(super) const ACCOUNT_ADJUST_LEVERAGE_INFO: &str = "/api/v5/account/adjust-leverage-info";
pub(super) const ACCOUNT_MAX_LOAN: &str = "/api/v5/account/max-loan";
pub(super) const ACCOUNT_TRADE_FEE: &str = "/api/v5/account/trade-fee";
pub(super) const ACCOUNT_INTEREST_ACCRUED: &str = "/api/v5/account/interest-accrued";
pub(super) const ACCOUNT_INTEREST_RATE: &str = "/api/v5/account/interest-rate";
pub(super) const ACCOUNT_SET_GREEKS: &str = "/api/v5/account/set-greeks";
pub(super) const ACCOUNT_MAX_WITHDRAWAL: &str = "/api/v5/account/max-withdrawal";
pub(super) const ACCOUNT_INTEREST_LIMITS: &str = "/api/v5/account/interest-limits";
pub(super) const ACCOUNT_SPOT_MANUAL_BORROW_REPAY: &str =
    "/api/v5/account/spot-manual-borrow-repay";
pub(super) const ACCOUNT_SET_AUTO_REPAY: &str = "/api/v5/account/set-auto-repay";
pub(super) const ACCOUNT_SPOT_BORROW_REPAY_HISTORY: &str =
    "/api/v5/account/spot-borrow-repay-history";
pub(super) const ACCOUNT_SET_AUTO_EARN: &str = "/api/v5/account/set-auto-earn";
pub(super) const SAVINGS_BALANCE: &str = "/api/v5/finance/savings/balance";
pub(super) const SAVINGS_PURCHASE_REDEMPT: &str = "/api/v5/finance/savings/purchase-redempt";
pub(super) const SAVINGS_SET_LENDING_RATE: &str = "/api/v5/finance/savings/set-lending-rate";
pub(super) const SAVINGS_LENDING_HISTORY: &str = "/api/v5/finance/savings/lending-history";
pub(super) const SAVINGS_PUBLIC_BORROW_INFO: &str = "/api/v5/finance/savings/lending-rate-summary";
pub(super) const SAVINGS_PUBLIC_BORROW_HISTORY: &str =
    "/api/v5/finance/savings/lending-rate-history";
pub(super) const STAKING_OFFERS: &str = "/api/v5/finance/staking-defi/offers";
pub(super) const STAKING_PURCHASE: &str = "/api/v5/finance/staking-defi/purchase";
pub(super) const STAKING_REDEEM: &str = "/api/v5/finance/staking-defi/redeem";
pub(super) const STAKING_CANCEL: &str = "/api/v5/finance/staking-defi/cancel";
pub(super) const STAKING_ACTIVE_ORDERS: &str = "/api/v5/finance/staking-defi/orders-active";
pub(super) const STAKING_ORDER_HISTORY: &str = "/api/v5/finance/staking-defi/orders-history";
pub(super) const ETH_STAKING_PRODUCT_INFO: &str = "/api/v5/finance/staking-defi/eth/product-info";
pub(super) const ETH_STAKING_PURCHASE: &str = "/api/v5/finance/staking-defi/eth/purchase";
pub(super) const ETH_STAKING_REDEEM: &str = "/api/v5/finance/staking-defi/eth/redeem";
pub(super) const ETH_STAKING_CANCEL_REDEEM: &str = "/api/v5/finance/staking-defi/eth/cancel-redeem";
pub(super) const ETH_STAKING_BALANCE: &str = "/api/v5/finance/staking-defi/eth/balance";
pub(super) const ETH_STAKING_HISTORY: &str =
    "/api/v5/finance/staking-defi/eth/purchase-redeem-history";
pub(super) const ETH_STAKING_APY_HISTORY: &str = "/api/v5/finance/staking-defi/eth/apy-history";
pub(super) const SOL_STAKING_PRODUCT_INFO: &str = "/api/v5/finance/staking-defi/sol/product-info";
pub(super) const SOL_STAKING_PURCHASE: &str = "/api/v5/finance/staking-defi/sol/purchase";
pub(super) const SOL_STAKING_REDEEM: &str = "/api/v5/finance/staking-defi/sol/redeem";
pub(super) const SOL_STAKING_BALANCE: &str = "/api/v5/finance/staking-defi/sol/balance";
pub(super) const SOL_STAKING_HISTORY: &str =
    "/api/v5/finance/staking-defi/sol/purchase-redeem-history";
pub(super) const SOL_STAKING_APY_HISTORY: &str = "/api/v5/finance/staking-defi/sol/apy-history";
pub(super) const FLEXIBLE_LOAN_BORROW_CURRENCIES: &str =
    "/api/v5/finance/flexible-loan/borrow-currencies";
pub(super) const FLEXIBLE_LOAN_COLLATERAL_ASSETS: &str =
    "/api/v5/finance/flexible-loan/collateral-assets";
pub(super) const FLEXIBLE_LOAN_MAX_LOAN: &str = "/api/v5/finance/flexible-loan/max-loan";
pub(super) const FLEXIBLE_LOAN_MAX_COLLATERAL_REDEEM: &str =
    "/api/v5/finance/flexible-loan/max-collateral-redeem-amount";
pub(super) const FLEXIBLE_LOAN_ADJUST_COLLATERAL: &str =
    "/api/v5/finance/flexible-loan/adjust-collateral";
pub(super) const FLEXIBLE_LOAN_INFO: &str = "/api/v5/finance/flexible-loan/loan-info";
pub(super) const FLEXIBLE_LOAN_HISTORY: &str = "/api/v5/finance/flexible-loan/loan-history";
pub(super) const FLEXIBLE_LOAN_INTEREST_ACCRUED: &str =
    "/api/v5/finance/flexible-loan/interest-accrued";
pub(super) const FLEXIBLE_LOAN_BORROW: &str = "/api/v5/finance/flexible-loan/borrow";
pub(super) const FLEXIBLE_LOAN_REPAY: &str = "/api/v5/finance/flexible-loan/repay";
pub(super) const FLEXIBLE_LOAN_EMODE_INFO: &str = "/api/v5/finance/flexible-loan/emode-info";
pub(super) const DUAL_INVESTMENT_CURRENCY_PAIRS: &str = "/api/v5/finance/sfp/dcd/currency-pair";
pub(super) const DUAL_INVESTMENT_PRODUCTS: &str = "/api/v5/finance/sfp/dcd/products";
pub(super) const DUAL_INVESTMENT_QUOTE: &str = "/api/v5/finance/sfp/dcd/quote";
pub(super) const DUAL_INVESTMENT_TRADE: &str = "/api/v5/finance/sfp/dcd/trade";
pub(super) const DUAL_INVESTMENT_REDEEM_QUOTE: &str = "/api/v5/finance/sfp/dcd/redeem-quote";
pub(super) const DUAL_INVESTMENT_REDEEM: &str = "/api/v5/finance/sfp/dcd/redeem";
pub(super) const DUAL_INVESTMENT_ORDER_STATUS: &str = "/api/v5/finance/sfp/dcd/order-status";
pub(super) const DUAL_INVESTMENT_ORDER_HISTORY: &str = "/api/v5/finance/sfp/dcd/order-history";
pub(super) const OKUSD_LIMITS: &str = "/api/v5/finance/okusd/limits";
pub(super) const OKUSD_ACCOUNT: &str = "/api/v5/finance/okusd/account";
pub(super) const OKUSD_RATE_HISTORY: &str = "/api/v5/finance/okusd/rate/history";
pub(super) const OKUSD_SUBSCRIBE_HISTORY: &str = "/api/v5/finance/okusd/subscribe/history";
pub(super) const OKUSD_REDEEM_HISTORY: &str = "/api/v5/finance/okusd/redeem/history";
pub(super) const OKUSD_REWARDS_HISTORY: &str = "/api/v5/finance/okusd/rewards/history";
pub(super) const OKUSD_SUBSCRIBE: &str = "/api/v5/finance/okusd/subscribe";
pub(super) const OKUSD_REDEEM: &str = "/api/v5/finance/okusd/redeem";
pub(super) const ASSET_CURRENCIES: &str = "/api/v5/asset/currencies";
pub(super) const ASSET_BALANCES: &str = "/api/v5/asset/balances";
pub(super) const ASSET_VALUATION: &str = "/api/v5/asset/asset-valuation";
pub(super) const ASSET_TRANSFER: &str = "/api/v5/asset/transfer";
pub(super) const ASSET_TRANSFER_STATE: &str = "/api/v5/asset/transfer-state";
pub(super) const SUBACCOUNT_LIST: &str = "/api/v5/users/subaccount/list";
pub(super) const SUBACCOUNT_TRADING_BALANCE: &str = "/api/v5/account/subaccount/balances";
pub(super) const SUBACCOUNT_FUNDING_BALANCE: &str = "/api/v5/asset/subaccount/balances";
pub(super) const SUBACCOUNT_BILLS: &str = "/api/v5/asset/subaccount/bills";
pub(super) const SUBACCOUNT_TRANSFER: &str = "/api/v5/asset/subaccount/transfer";
pub(super) const ENTRUSTED_SUBACCOUNT_LIST: &str = "/api/v5/users/entrust-subaccount-list";
pub(super) const SUBACCOUNT_INTEREST_LIMITS: &str = "/api/v5/account/subaccount/interest-limits";
pub(super) const ASSET_BILLS: &str = "/api/v5/asset/bills";
pub(super) const ASSET_DEPOSIT_ADDRESS: &str = "/api/v5/asset/deposit-address";
pub(super) const ASSET_DEPOSIT_HISTORY: &str = "/api/v5/asset/deposit-history";
pub(super) const ASSET_DEPOSIT_WITHDRAW_STATUS: &str = "/api/v5/asset/deposit-withdraw-status";
pub(super) const ASSET_EXCHANGE_LIST: &str = "/api/v5/asset/exchange-list";
pub(super) const ASSET_MONTHLY_STATEMENT: &str = "/api/v5/asset/monthly-statement";
pub(super) const ASSET_CONVERT_CURRENCIES: &str = "/api/v5/asset/convert/currencies";
pub(super) const ASSET_CONVERT_HISTORY: &str = "/api/v5/asset/convert/history";
pub(super) const TRADE_ORDER: &str = "/api/v5/trade/order";
pub(super) const TRADE_ORDER_PRECHECK: &str = "/api/v5/trade/order-precheck";
pub(super) const TRADE_CANCEL_ALL_AFTER: &str = "/api/v5/trade/cancel-all-after";
pub(super) const TRADE_BATCH_ORDERS: &str = "/api/v5/trade/batch-orders";
pub(super) const TRADE_CANCEL_ORDER: &str = "/api/v5/trade/cancel-order";
pub(super) const TRADE_CANCEL_BATCH_ORDERS: &str = "/api/v5/trade/cancel-batch-orders";
pub(super) const TRADE_AMEND_ORDER: &str = "/api/v5/trade/amend-order";
pub(super) const TRADE_AMEND_BATCH_ORDERS: &str = "/api/v5/trade/amend-batch-orders";
pub(super) const TRADE_CLOSE_POSITION: &str = "/api/v5/trade/close-position";
pub(super) const TRADE_ORDERS_PENDING: &str = "/api/v5/trade/orders-pending";
pub(super) const TRADE_ORDERS_HISTORY: &str = "/api/v5/trade/orders-history";
pub(super) const TRADE_ORDERS_HISTORY_ARCHIVE: &str = "/api/v5/trade/orders-history-archive";
pub(super) const TRADE_FILLS: &str = "/api/v5/trade/fills";
pub(super) const TRADE_FILLS_HISTORY: &str = "/api/v5/trade/fills-history";
pub(super) const TRADE_ACCOUNT_RATE_LIMIT: &str = "/api/v5/trade/account-rate-limit";
