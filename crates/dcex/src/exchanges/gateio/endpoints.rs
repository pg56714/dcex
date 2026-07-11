pub(super) const BASE_URL: &str = "https://api.gateio.ws";
pub(super) const API_PREFIX: &str = "/api/v4";

pub(super) const WALLET_TOTAL_BALANCE: &str = "/wallet/total_balance";
pub(super) const WALLET_TRANSFERS: &str = "/wallet/transfers";
pub(super) const UNIFIED_ACCOUNTS: &str = "/unified/accounts";

pub(super) const FUTURES_CONTRACTS: &str = "/futures/{settle}/contracts";
pub(super) const FUTURES_CONTRACT: &str = "/futures/{settle}/contracts/{contract}";
pub(super) const FUTURES_ACCOUNT: &str = "/futures/{settle}/accounts";
pub(super) const FUTURES_ACCOUNT_BOOK: &str = "/futures/{settle}/account_book";
pub(super) const FUTURES_FEE: &str = "/futures/{settle}/fee";
pub(super) const FUTURES_POSITIONS: &str = "/futures/{settle}/positions";
pub(super) const FUTURES_POSITION: &str = "/futures/{settle}/positions/{contract}";
pub(super) const FUTURES_POSITION_LEVERAGE: &str =
    "/futures/{settle}/positions/{contract}/leverage";
pub(super) const FUTURES_DUAL_MODE: &str = "/futures/{settle}/dual_mode";
pub(super) const FUTURES_ORDERS: &str = "/futures/{settle}/orders";
pub(super) const FUTURES_BATCH_ORDERS: &str = "/futures/{settle}/batch_orders";
pub(super) const FUTURES_ORDER: &str = "/futures/{settle}/orders/{order_id}";
pub(super) const FUTURES_MY_TRADES: &str = "/futures/{settle}/my_trades";
pub(super) const FUTURES_POSITION_CLOSE: &str = "/futures/{settle}/position_close";
pub(super) const FUTURES_AUTO_DELEVERAGES: &str = "/futures/{settle}/auto_deleverages";
pub(super) const FUTURES_ORDER_BOOK: &str = "/futures/{settle}/order_book";
pub(super) const FUTURES_CANDLESTICKS: &str = "/futures/{settle}/candlesticks";
pub(super) const FUTURES_TICKERS: &str = "/futures/{settle}/tickers";
pub(super) const FUTURES_FUNDING_RATE: &str = "/futures/{settle}/funding_rate";
pub(super) const FUTURES_CONTRACT_STATS: &str = "/futures/{settle}/contract_stats";

pub(super) const DELIVERY_CONTRACTS: &str = "/delivery/{settle}/contracts";
pub(super) const DELIVERY_ACCOUNT: &str = "/delivery/{settle}/accounts";
pub(super) const DELIVERY_ACCOUNT_BOOK: &str = "/delivery/{settle}/account_book";
pub(super) const DELIVERY_POSITIONS: &str = "/delivery/{settle}/positions";
pub(super) const DELIVERY_POSITION: &str = "/delivery/{settle}/positions/{contract}";
pub(super) const DELIVERY_POSITION_LEVERAGE: &str =
    "/delivery/{settle}/positions/{contract}/leverage";
pub(super) const DELIVERY_ORDERS: &str = "/delivery/{settle}/orders";
pub(super) const DELIVERY_ORDER: &str = "/delivery/{settle}/orders/{order_id}";
pub(super) const DELIVERY_MY_TRADES: &str = "/delivery/{settle}/my_trades";
pub(super) const DELIVERY_POSITION_CLOSE: &str = "/delivery/{settle}/position_close";
pub(super) const DELIVERY_ORDER_BOOK: &str = "/delivery/{settle}/order_book";
pub(super) const DELIVERY_CANDLESTICKS: &str = "/delivery/{settle}/candlesticks";
pub(super) const DELIVERY_TICKERS: &str = "/delivery/{settle}/tickers";

pub(super) const SPOT_CURRENCY_PAIRS: &str = "/spot/currency_pairs";
pub(super) const SPOT_ORDER_BOOK: &str = "/spot/order_book";
pub(super) const SPOT_CANDLESTICKS: &str = "/spot/candlesticks";
pub(super) const SPOT_TICKERS: &str = "/spot/tickers";
pub(super) const SPOT_ACCOUNTS: &str = "/spot/accounts";
pub(super) const SPOT_ACCOUNT_BOOK: &str = "/spot/account_book";
pub(super) const SPOT_FEE: &str = "/spot/fee";
pub(super) const SPOT_BATCH_FEE: &str = "/spot/batch_fee";
pub(super) const SPOT_OPEN_ORDERS: &str = "/spot/open_orders";
pub(super) const SPOT_ORDERS: &str = "/spot/orders";
pub(super) const SPOT_ORDER: &str = "/spot/orders/{order_id}";
pub(super) const SPOT_MY_TRADES: &str = "/spot/my_trades";

pub(super) fn api_path(path: &str) -> String {
    format!("{API_PREFIX}{path}")
}

pub(super) fn market_path(
    market: &str,
    futures_path: &str,
    delivery_path: &str,
) -> Option<&'static str> {
    match market {
        "futures" => Some(match futures_path {
            "contracts" => FUTURES_CONTRACTS,
            "order_book" => FUTURES_ORDER_BOOK,
            "candlesticks" => FUTURES_CANDLESTICKS,
            "tickers" => FUTURES_TICKERS,
            "orders" => FUTURES_ORDERS,
            "order" => FUTURES_ORDER,
            "positions" => FUTURES_POSITIONS,
            "position" => FUTURES_POSITION,
            "my_trades" => FUTURES_MY_TRADES,
            _ => return None,
        }),
        "delivery" => Some(match delivery_path {
            "contracts" => DELIVERY_CONTRACTS,
            "order_book" => DELIVERY_ORDER_BOOK,
            "candlesticks" => DELIVERY_CANDLESTICKS,
            "tickers" => DELIVERY_TICKERS,
            "orders" => DELIVERY_ORDERS,
            "order" => DELIVERY_ORDER,
            "positions" => DELIVERY_POSITIONS,
            "position" => DELIVERY_POSITION,
            "my_trades" => DELIVERY_MY_TRADES,
            _ => return None,
        }),
        _ => None,
    }
}

pub(super) fn fill_settle(path: &str, settle: &str) -> String {
    path.replace("{settle}", settle)
}

pub(super) fn fill_contract(path: &str, settle: &str, contract: &str) -> String {
    fill_settle(path, settle).replace("{contract}", contract)
}

pub(super) fn fill_order(path: &str, settle: &str, order_id: &str) -> String {
    fill_settle(path, settle).replace("{order_id}", order_id)
}

pub(super) fn fill_spot_order(order_id: &str) -> String {
    SPOT_ORDER.replace("{order_id}", order_id)
}
