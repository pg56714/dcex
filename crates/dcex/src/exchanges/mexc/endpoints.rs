pub(super) const BASE_URL: &str = "https://api.mexc.com";
pub(super) const CONTRACT_BASE_URL: &str = "https://api.mexc.com";

pub(super) const SPOT_PING: &str = "/api/v3/ping";
pub(super) const SPOT_TIME: &str = "/api/v3/time";
pub(super) const SPOT_DEFAULT_SYMBOLS: &str = "/api/v3/defaultSymbols";
pub(super) const SPOT_EXCHANGE_INFO: &str = "/api/v3/exchangeInfo";
pub(super) const SPOT_ORDERBOOK: &str = "/api/v3/depth";
pub(super) const SPOT_RECENT_TRADES: &str = "/api/v3/trades";
pub(super) const SPOT_AGG_TRADES: &str = "/api/v3/aggTrades";
pub(super) const SPOT_KLINES: &str = "/api/v3/klines";
pub(super) const SPOT_AVG_PRICE: &str = "/api/v3/avgPrice";
pub(super) const SPOT_TICKER_24HR: &str = "/api/v3/ticker/24hr";
pub(super) const SPOT_TICKER_PRICE: &str = "/api/v3/ticker/price";
pub(super) const SPOT_BOOK_TICKER: &str = "/api/v3/ticker/bookTicker";

pub(super) const SPOT_KYC_STATUS: &str = "/api/v3/kyc/status";
pub(super) const SPOT_SELF_SYMBOLS: &str = "/api/v3/selfSymbols";
pub(super) const SPOT_ACCOUNT: &str = "/api/v3/account";
pub(super) const SPOT_MX_DEDUCT_ENABLE: &str = "/api/v3/mxDeduct/enable";
pub(super) const SPOT_SYMBOL_COMMISSION: &str = "/api/v3/tradeFee";
pub(super) const SPOT_CURRENCY_INFO: &str = "/api/v3/capital/config/getall";
pub(super) const SPOT_DEPOSIT_HISTORY: &str = "/api/v3/capital/deposit/hisrec";
pub(super) const SPOT_WITHDRAW_HISTORY: &str = "/api/v3/capital/withdraw/history";
pub(super) const SPOT_DEPOSIT_ADDRESS: &str = "/api/v3/capital/deposit/address";
pub(super) const SPOT_USER_UNIVERSAL_TRANSFER: &str = "/api/v3/capital/transfer";
pub(super) const SPOT_USER_UNIVERSAL_TRANSFER_BY_ID: &str = "/api/v3/capital/transfer/tranId";
pub(super) const SPOT_INTERNAL_TRANSFER_HISTORY: &str = "/api/v3/capital/transfer/internal";

pub(super) const SPOT_TEST_ORDER: &str = "/api/v3/order/test";
pub(super) const SPOT_ORDER: &str = "/api/v3/order";
pub(super) const SPOT_BATCH_ORDERS: &str = "/api/v3/batchOrders";
pub(super) const SPOT_OPEN_ORDERS: &str = "/api/v3/openOrders";
pub(super) const SPOT_ALL_ORDERS: &str = "/api/v3/allOrders";
pub(super) const SPOT_MY_TRADES: &str = "/api/v3/myTrades";

pub(super) const CONTRACT_PING: &str = "/api/v1/contract/ping";
pub(super) const CONTRACT_DETAIL: &str = "/api/v1/contract/detail";
pub(super) const CONTRACT_TICKER: &str = "/api/v1/contract/ticker";
pub(super) const CONTRACT_RISK_REVERSE: &str = "/api/v1/contract/risk_reverse";
pub(super) const CONTRACT_RISK_REVERSE_HISTORY: &str = "/api/v1/contract/risk_reverse/history";
pub(super) const CONTRACT_FUNDING_RATE_HISTORY: &str = "/api/v1/contract/funding_rate/history";

pub(super) const CONTRACT_ASSETS: &str = "/api/v1/private/account/assets";
pub(super) const CONTRACT_ASSET: &str = "/api/v1/private/account/asset/{currency}";
pub(super) const CONTRACT_TRANSFER_RECORDS: &str = "/api/v1/private/account/transfer_record";
pub(super) const CONTRACT_HISTORY_POSITIONS: &str =
    "/api/v1/private/position/list/history_positions";
pub(super) const CONTRACT_OPEN_POSITIONS: &str = "/api/v1/private/position/open_positions";
pub(super) const CONTRACT_FUNDING_RECORDS: &str = "/api/v1/private/position/funding_records";
pub(super) const CONTRACT_RISK_LIMITS: &str = "/api/v1/private/account/risk_limit";
pub(super) const CONTRACT_TRADING_FEE_RATE: &str = "/api/v1/private/account/tiered_fee_rate";
pub(super) const CONTRACT_LEVERAGE: &str = "/api/v1/private/position/leverage";
pub(super) const CONTRACT_CHANGE_MARGIN: &str = "/api/v1/private/position/change_margin";
pub(super) const CONTRACT_CHANGE_LEVERAGE: &str = "/api/v1/private/position/change_leverage";
pub(super) const CONTRACT_POSITION_MODE: &str = "/api/v1/private/position/position_mode";
pub(super) const CONTRACT_CHANGE_POSITION_MODE: &str =
    "/api/v1/private/position/change_position_mode";

pub(super) const CONTRACT_CREATE_ORDER: &str = "/api/v1/private/order/create";
pub(super) const CONTRACT_CANCEL_ORDERS: &str = "/api/v1/private/order/cancel";
pub(super) const CONTRACT_CANCEL_ORDER_WITH_EXTERNAL_ID: &str =
    "/api/v1/private/order/cancel_with_external";
pub(super) const CONTRACT_CANCEL_ALL_ORDERS: &str = "/api/v1/private/order/cancel_all";
pub(super) const CONTRACT_OPEN_ORDERS: &str = "/api/v1/private/order/list/open_orders/{symbol}";
pub(super) const CONTRACT_HISTORY_ORDERS: &str = "/api/v1/private/order/list/history_orders";
pub(super) const CONTRACT_EXTERNAL_ORDER: &str =
    "/api/v1/private/order/external/{symbol}/{external_oid}";
pub(super) const CONTRACT_ORDER: &str = "/api/v1/private/order/get/{order_id}";
pub(super) const CONTRACT_BATCH_QUERY: &str = "/api/v1/private/order/batch_query";
pub(super) const CONTRACT_ORDER_DEAL_DETAILS: &str =
    "/api/v1/private/order/deal_details/{order_id}";
pub(super) const CONTRACT_ORDER_DEALS: &str = "/api/v1/private/order/list/order_deals";
pub(super) const CONTRACT_PLAN_ORDERS: &str = "/api/v1/private/planorder/list/orders";
pub(super) const CONTRACT_PLACE_PLAN_ORDER: &str = "/api/v1/private/planorder/place";
pub(super) const CONTRACT_CANCEL_PLAN_ORDERS: &str = "/api/v1/private/planorder/cancel";
pub(super) const CONTRACT_CANCEL_ALL_PLAN_ORDERS: &str = "/api/v1/private/planorder/cancel_all";
pub(super) const CONTRACT_STOP_ORDERS: &str = "/api/v1/private/stoporder/list/orders";
