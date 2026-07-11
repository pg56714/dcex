pub(super) const SPOT_BASE_URL: &str = "https://api-cloud.bitmart.com";
pub(super) const FUTURES_BASE_URL: &str = "https://api-cloud-v2.bitmart.com";

pub(super) const SPOT_CURRENCIES: &str = "/spot/v1/currencies";
pub(super) const SPOT_SYMBOLS: &str = "/spot/v1/symbols";
pub(super) const SPOT_SYMBOL_DETAILS: &str = "/spot/v1/symbols/details";
pub(super) const SPOT_TICKERS: &str = "/spot/quotation/v3/tickers";
pub(super) const SPOT_TICKER: &str = "/spot/quotation/v3/ticker";
pub(super) const SPOT_KLINE: &str = "/spot/quotation/v3/lite-klines";

pub(super) const ACCOUNT_BALANCE: &str = "/account/v1/wallet";
pub(super) const ACCOUNT_CURRENCIES: &str = "/account/v1/currencies";
pub(super) const SPOT_WALLET: &str = "/spot/v1/wallet";
pub(super) const SPOT_TRADE_FEE: &str = "/spot/v1/trade_fee";
pub(super) const DEPOSIT_ADDRESS: &str = "/account/v1/deposit/address";

pub(super) const SPOT_SUBMIT_ORDER: &str = "/spot/v2/submit_order";
pub(super) const SPOT_CANCEL_ORDER: &str = "/spot/v3/cancel_order";
pub(super) const SPOT_CANCEL_ALL_ORDERS: &str = "/spot/v4/cancel_all";
pub(super) const SPOT_QUERY_ORDER_BY_ID: &str = "/spot/v4/query/order";
pub(super) const SPOT_QUERY_ORDER_BY_CLIENT_ID: &str = "/spot/v4/query/client-order";
pub(super) const SPOT_OPEN_ORDERS: &str = "/spot/v4/query/open-orders";
pub(super) const SPOT_ACCOUNT_ORDERS: &str = "/spot/v4/query/history-orders";
pub(super) const SPOT_ACCOUNT_TRADE_LIST: &str = "/spot/v4/query/trades";
pub(super) const SPOT_ORDER_TRADE_LIST: &str = "/spot/v4/query/order-trades";
pub(super) const SPOT_ALGO_SUBMIT_ORDER: &str = "/spot/v4/algo/submit_order";
pub(super) const SPOT_ALGO_CANCEL_ORDER: &str = "/spot/v4/algo/cancel_order";
pub(super) const SPOT_ALGO_CANCEL_ALL: &str = "/spot/v4/algo/cancel_all";
pub(super) const SPOT_ALGO_ORDER: &str = "/spot/v4/query/algo/order";
pub(super) const SPOT_ALGO_CLIENT_ORDER: &str = "/spot/v4/query/algo/client-order";
pub(super) const SPOT_ALGO_OPEN_ORDERS: &str = "/spot/v4/query/algo/open-orders";

pub(super) const FUTURES_CONTRACT_DETAILS: &str = "/contract/public/details";
pub(super) const FUTURES_DEPTH: &str = "/contract/public/depth";
pub(super) const FUTURES_KLINE: &str = "/contract/public/kline";
pub(super) const FUTURES_FUNDING_RATE: &str = "/contract/public/funding-rate";
pub(super) const FUTURES_FUNDING_RATE_HISTORY: &str = "/contract/public/funding-rate-history";
pub(super) const FUTURES_OPEN_INTEREST: &str = "/contract/public/open-interest";
pub(super) const FUTURES_MARK_PRICE_KLINE: &str = "/contract/public/markprice-kline";
pub(super) const FUTURES_LEVERAGE_BRACKET: &str = "/contract/public/leverage-bracket";

pub(super) const FUTURES_CONTRACT_ASSETS: &str = "/contract/private/assets-detail";
pub(super) const FUTURES_TRADE_FEE_RATE: &str = "/contract/private/trade-fee-rate";
pub(super) const FUTURES_SUBMIT_ORDER: &str = "/contract/private/submit-order";
pub(super) const FUTURES_MODIFY_LIMIT_ORDER: &str = "/contract/private/modify-limit-order";
pub(super) const FUTURES_CANCEL_ORDER: &str = "/contract/private/cancel-order";
pub(super) const FUTURES_CANCEL_ALL_ORDERS: &str = "/contract/private/cancel-orders";
pub(super) const FUTURES_TRANSFER: &str = "/account/v1/transfer-contract";
pub(super) const FUTURES_SUBMIT_LEVERAGE: &str = "/contract/private/submit-leverage";
pub(super) const FUTURES_ORDER_DETAIL: &str = "/contract/private/order";
pub(super) const FUTURES_ORDER_HISTORY: &str = "/contract/private/order-history";
pub(super) const FUTURES_OPEN_ORDERS: &str = "/contract/private/get-open-orders";
pub(super) const FUTURES_POSITION: &str = "/contract/private/position";
pub(super) const FUTURES_ORDER_TRADE: &str = "/contract/private/trades";
pub(super) const FUTURES_TRANSACTION_HISTORY: &str = "/contract/private/transaction-history";
pub(super) const FUTURES_TRANSFER_LIST: &str = "/account/v1/transfer-contract-list";
