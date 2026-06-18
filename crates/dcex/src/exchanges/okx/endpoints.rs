pub(super) const BASE_URL: &str = "https://openapi.okx.com";
pub(super) const PUBLIC_INSTRUMENTS: &str = "/api/v5/public/instruments";
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
pub(super) const ASSET_CURRENCIES: &str = "/api/v5/asset/currencies";
pub(super) const ASSET_BALANCES: &str = "/api/v5/asset/balances";
pub(super) const ASSET_VALUATION: &str = "/api/v5/asset/asset-valuation";
pub(super) const ASSET_TRANSFER: &str = "/api/v5/asset/transfer";
pub(super) const ASSET_TRANSFER_STATE: &str = "/api/v5/asset/transfer-state";
pub(super) const ASSET_BILLS: &str = "/api/v5/asset/bills";
pub(super) const ASSET_DEPOSIT_ADDRESS: &str = "/api/v5/asset/deposit-address";
pub(super) const ASSET_DEPOSIT_HISTORY: &str = "/api/v5/asset/deposit-history";
pub(super) const ASSET_DEPOSIT_WITHDRAW_STATUS: &str = "/api/v5/asset/deposit-withdraw-status";
pub(super) const ASSET_EXCHANGE_LIST: &str = "/api/v5/asset/exchange-list";
pub(super) const ASSET_MONTHLY_STATEMENT: &str = "/api/v5/asset/monthly-statement";
pub(super) const ASSET_CONVERT_CURRENCIES: &str = "/api/v5/asset/convert/currencies";
pub(super) const ASSET_CONVERT_HISTORY: &str = "/api/v5/asset/convert/history";
pub(super) const TRADE_ORDER: &str = "/api/v5/trade/order";
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
