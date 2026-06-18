pub(super) const BASE_URL: &str = "https://www.bitmex.com";

pub(super) const INSTRUMENT_INFO: &str = "/api/v1/instrument";
pub(super) const ACTIVE_INSTRUMENTS: &str = "/api/v1/instrument/active";
pub(super) const ORDERBOOK: &str = "/api/v1/orderBook/L2";
pub(super) const TRADE: &str = "/api/v1/trade";
pub(super) const TICKER: &str = "/api/v1/quote/bucketed";
pub(super) const KLINE: &str = "/api/v1/trade/bucketed";
pub(super) const FUNDING: &str = "/api/v1/funding";
pub(super) const LIQUIDATION: &str = "/api/v1/liquidation";

pub(super) const ACCOUNT_INFO: &str = "/api/v1/user/wallet";

pub(super) const GET_POSITIONS: &str = "/api/v1/position";
pub(super) const SWITCH_MODE: &str = "/api/v1/position/isolate";
pub(super) const LEVERAGE: &str = "/api/v1/position/leverage";
pub(super) const MARGINING_MODE: &str = "/api/v1/user/marginingMode";
pub(super) const GET_MARGIN: &str = "/api/v1/user/margin";

pub(super) const PLACE_ORDER: &str = "/api/v2/order";
pub(super) const AMEND_ORDER: &str = "/api/v2/order";
pub(super) const CANCEL_ORDER: &str = "/api/v2/order";
pub(super) const CANCEL_ALL_ORDERS: &str = "/api/v2/order/all";
pub(super) const QUERY_ORDER: &str = "/api/v1/order";

pub(super) const GET_EXECUTIONS: &str = "/api/v1/execution";
pub(super) const GET_TRADE_HISTORY: &str = "/api/v1/execution/tradeHistory";
pub(super) const GET_TRADING_VOLUME: &str = "/api/v1/user/tradingVolume";
