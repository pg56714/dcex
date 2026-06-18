pub(super) const BASE_URL: &str = "https://open-api.bingx.com";

pub(super) const SWAP_ACCOUNT_BALANCE: &str = "/openApi/swap/v3/user/balance";
pub(super) const SWAP_OPEN_POSITIONS: &str = "/openApi/swap/v2/user/positions";
pub(super) const SWAP_FUND_FLOW: &str = "/openApi/swap/v2/user/income";
pub(super) const SWAP_LISTEN_KEY: &str = "/openApi/user/auth/userDataStream";

pub(super) const SPOT_ACCOUNT_BALANCE: &str = "/openApi/spot/v1/account/balance";

pub(super) const FUND_ACCOUNT_BALANCE: &str = "/openApi/fund/v1/account/balance";
pub(super) const FUND_ALL_ACCOUNT_BALANCE: &str = "/openApi/account/v1/allAccountBalance";
pub(super) const FUND_ACCOUNT_UID: &str = "/openApi/account/v1/uid";
pub(super) const FUND_API_KEY_INFO: &str = "/openApi/account/v1/apiKey/query";

pub(super) const TRANSFERABLE_COINS: &str = "/openApi/api/asset/v1/transfer/supportCoins";
pub(super) const ASSET_TRANSFER: &str = "/openApi/api/asset/v1/transfer";
pub(super) const TRANSFER_RECORDS: &str = "/openApi/api/v3/asset/transferRecord";

pub(super) const SWAP_PLACE_ORDER: &str = "/openApi/swap/v2/trade/order";
pub(super) const SWAP_TEST_ORDER: &str = "/openApi/swap/v2/trade/order/test";
pub(super) const SWAP_PLACE_BATCH_ORDER: &str = "/openApi/swap/v2/trade/batchOrders";
pub(super) const SWAP_CANCEL_BATCH_ORDER: &str = "/openApi/swap/v2/trade/batchOrders";
pub(super) const SWAP_CANCEL_ALL_OPEN_ORDERS: &str = "/openApi/swap/v2/trade/allOpenOrders";
pub(super) const SWAP_REPLACE_ORDER: &str = "/openApi/swap/v1/trade/cancelReplace";
pub(super) const SWAP_CLOSE_POSITION: &str = "/openApi/swap/v1/trade/closePosition";
pub(super) const SWAP_CLOSE_ALL_POSITIONS: &str = "/openApi/swap/v2/trade/closeAllPositions";
pub(super) const SWAP_QUERY_ALL_OPEN_ORDERS: &str = "/openApi/swap/v2/trade/openOrders";
pub(super) const SWAP_QUERY_ORDER_HISTORY: &str = "/openApi/swap/v2/trade/allOrders";
pub(super) const SWAP_CHANGE_MARGIN_TYPE: &str = "/openApi/swap/v2/trade/marginType";
pub(super) const SWAP_SET_LEVERAGE: &str = "/openApi/swap/v2/trade/leverage";
pub(super) const SWAP_SET_POSITION_MODE: &str = "/openApi/swap/v1/positionSide/dual";

pub(super) const SPOT_PLACE_ORDER: &str = "/openApi/spot/v1/trade/order";
pub(super) const SPOT_PLACE_BATCH_ORDER: &str = "/openApi/spot/v1/trade/batchOrders";
pub(super) const SPOT_CANCEL_ORDER: &str = "/openApi/spot/v1/trade/cancel";
pub(super) const SPOT_CANCEL_BATCH_ORDERS: &str = "/openApi/spot/v1/trade/cancelOrders";
pub(super) const SPOT_CANCEL_OPEN_ORDERS: &str = "/openApi/spot/v1/trade/cancelOpenOrders";
pub(super) const SPOT_QUERY_ORDER: &str = "/openApi/spot/v1/trade/query";
pub(super) const SPOT_QUERY_OPEN_ORDERS: &str = "/openApi/spot/v1/trade/openOrders";
pub(super) const SPOT_QUERY_ORDER_HISTORY: &str = "/openApi/spot/v1/trade/historyOrders";
pub(super) const SPOT_QUERY_MY_TRADES: &str = "/openApi/spot/v1/trade/myTrades";
pub(super) const SPOT_COMMISSION_RATE: &str = "/openApi/spot/v1/user/commissionRate";

pub(super) const SWAP_INSTRUMENT_INFO: &str = "/openApi/swap/v2/quote/contracts";
pub(super) const SWAP_ORDERBOOK: &str = "/openApi/swap/v2/quote/depth";
pub(super) const SWAP_PUBLIC_TRADE: &str = "/openApi/swap/v2/quote/trades";
pub(super) const SWAP_KLINE: &str = "/openApi/swap/v3/quote/klines";
pub(super) const SWAP_TICKER: &str = "/openApi/swap/v2/quote/ticker";
pub(super) const SWAP_OPEN_INTEREST: &str = "/openApi/swap/v2/quote/openInterest";
pub(super) const SWAP_MARK_PRICE_KLINE: &str = "/openApi/swap/v1/market/markPriceKlines";

pub(super) const SPOT_SYMBOLS: &str = "/openApi/spot/v1/common/symbols";
pub(super) const SPOT_ORDERBOOK: &str = "/openApi/spot/v1/market/depth";
pub(super) const SPOT_ORDERBOOK_V2: &str = "/openApi/spot/v2/market/depth";
pub(super) const SPOT_PUBLIC_TRADE: &str = "/openApi/spot/v1/market/trades";
pub(super) const SPOT_KLINE: &str = "/openApi/spot/v1/market/kline";
pub(super) const SPOT_KLINE_V2: &str = "/openApi/spot/v2/market/kline";
pub(super) const SPOT_TICKER: &str = "/openApi/spot/v1/ticker/24hr";
pub(super) const SPOT_BOOK_TICKER: &str = "/openApi/spot/v1/ticker/bookTicker";
pub(super) const SPOT_PRICE_TICKER: &str = "/openApi/spot/v2/ticker/price";
