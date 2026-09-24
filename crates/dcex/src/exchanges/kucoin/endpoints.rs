pub(super) const SPOT_BASE_URL: &str = "https://api.kucoin.com";
pub(super) const FUTURES_BASE_URL: &str = "https://api-futures.kucoin.com";

pub(super) const WS_PUBLIC_TOKEN: &str = "/api/v1/bullet-public";
pub(super) const WS_PRIVATE_TOKEN: &str = "/api/v1/bullet-private";

pub(super) const SPOT_INSTRUMENT_INFO: &str = "/api/v2/symbols";
pub(super) const SPOT_TICKER: &str = "/api/v1/market/orderbook/level1";
pub(super) const SPOT_ALL_TICKERS: &str = "/api/v1/market/allTickers";
pub(super) const SPOT_ORDERBOOK: &str = "/api/v1/market/orderbook/level2_20";
pub(super) const SPOT_PUBLIC_TRADES: &str = "/api/v1/market/histories";
pub(super) const SPOT_KLINE: &str = "/api/v1/market/candles";

pub(super) const SPOT_ACCOUNT_BALANCE: &str = "/api/v1/accounts";
pub(super) const SPOT_TRANSFER_QUOTAS: &str = "/api/v1/accounts/transferable";
pub(super) const SPOT_FLEX_TRANSFER: &str = "/api/v3/accounts/universal-transfer";
pub(super) const SUBACCOUNT_LIST: &str = "/api/v2/sub/user";
pub(super) const SUBACCOUNT_BALANCE: &str = "/api/v1/sub-accounts/{subUserId}";
pub(super) const SPOT_SUBACCOUNT_BALANCES: &str = "/api/v2/sub-accounts";
pub(super) const FUTURES_SUBACCOUNT_BALANCES: &str = "/api/v1/account-overview-all";
pub(super) const UTA_SUBACCOUNT_LIST: &str = "/api/ua/v2/user/sub-account-list";
pub(super) const UTA_SUBACCOUNT_CURRENCY_ASSETS: &str = "/api/ua/v2/sub-account/balance";
pub(super) const SPOT_TRADE_FEES: &str = "/api/v1/trade-fees";
pub(super) const UTA_FEE_RATES: &str = "/api/ua/v1/user/fee-rate";
pub(super) const UTA_POSITION_TIERS: &str = "/api/ua/v1/market/position-tiers";

pub(super) const CROSS_MARGIN_SYMBOLS: &str = "/api/v3/margin/symbols";
pub(super) const ISOLATED_MARGIN_SYMBOLS: &str = "/api/v1/isolated/symbols";
pub(super) const MARGIN_COLLATERAL_RATIO: &str = "/api/v3/margin/collateralRatio";
pub(super) const MARGIN_AVAILABLE_INVENTORY: &str = "/api/v3/margin/available-inventory";
pub(super) const CROSS_MARGIN_ACCOUNT: &str = "/api/v3/margin/accounts";
pub(super) const ISOLATED_MARGIN_ACCOUNT: &str = "/api/v3/isolated/accounts";
pub(super) const MARGIN_BORROW_RATE: &str = "/api/v3/margin/borrowRate";
pub(super) const MARGIN_BORROW: &str = "/api/v3/margin/borrow";
pub(super) const MARGIN_REPAY: &str = "/api/v3/margin/repay";
pub(super) const MARGIN_INTEREST: &str = "/api/v3/margin/interest";
pub(super) const MARGIN_MODIFY_LEVERAGE: &str = "/api/v3/position/update-user-leverage";
pub(super) const MARGIN_LOAN_MARKET: &str = "/api/v3/project/list";
pub(super) const MARGIN_LOAN_MARKET_RATE: &str = "/api/v3/project/marketInterestRate";
pub(super) const MARGIN_LENDING_PURCHASE: &str = "/api/v3/purchase";
pub(super) const MARGIN_LENDING_MODIFY_PURCHASE: &str = "/api/v3/lend/purchase/update";
pub(super) const MARGIN_LENDING_PURCHASE_ORDERS: &str = "/api/v3/purchase/orders";
pub(super) const MARGIN_LENDING_REDEEM: &str = "/api/v3/redeem";
pub(super) const MARGIN_LENDING_REDEEM_ORDERS: &str = "/api/v3/redeem/orders";

pub(super) const EARN_ORDERS: &str = "/api/v1/earn/orders";
pub(super) const EARN_REDEEM_PREVIEW: &str = "/api/v1/earn/redeem-preview";
pub(super) const EARN_SAVINGS_PRODUCTS: &str = "/api/v1/earn/saving/products";
pub(super) const EARN_PROMOTION_PRODUCTS: &str = "/api/v1/earn/promotion/products";
pub(super) const EARN_STAKING_PRODUCTS: &str = "/api/v1/earn/staking/products";
pub(super) const EARN_KCS_STAKING_PRODUCTS: &str = "/api/v1/earn/kcs-staking/products";
pub(super) const EARN_ETH_STAKING_PRODUCTS: &str = "/api/v1/earn/eth-staking/products";
pub(super) const EARN_ACCOUNT_HOLDINGS: &str = "/api/v1/earn/hold-assets";
pub(super) const STRUCTURED_EARN_ORDERS: &str = "/api/v1/struct-earn/orders";
pub(super) const DUAL_INVESTMENT_PRODUCTS: &str = "/api/v1/struct-earn/dual/products";

pub(super) const SPOT_PLACE_ORDER: &str = "/api/v1/hf/orders";
pub(super) const SPOT_BATCH_ORDERS: &str = "/api/v1/hf/orders/multi";
pub(super) const SPOT_CANCEL_ORDER: &str = "/api/v1/hf/orders/{orderId}";
pub(super) const SPOT_CANCEL_ALL_ORDERS_BY_SYMBOL: &str = "/api/v1/hf/orders";
pub(super) const SPOT_CANCEL_ALL_ORDERS: &str = "/api/v1/hf/orders/cancelAll";
pub(super) const SPOT_OPEN_ORDERS: &str = "/api/v1/hf/orders/active/page";
pub(super) const SPOT_TRADE_HISTORY: &str = "/api/v1/hf/fills";

pub(super) const FUTURES_CONTRACTS: &str = "/api/v1/contracts/active";
pub(super) const FUTURES_TICKER: &str = "/api/v1/ticker";
pub(super) const FUTURES_ORDERBOOK: &str = "/api/v1/level2/snapshot";
pub(super) const FUTURES_PUBLIC_TRADES: &str = "/api/v1/trade/history";
pub(super) const FUTURES_KLINE: &str = "/api/v1/kline/query";
pub(super) const FUTURES_OPEN_INTEREST: &str = "/api/ua/v1/market/open-interest";

pub(super) const FUTURES_ACCOUNT_OVERVIEW: &str = "/api/v1/account-overview";
pub(super) const FUTURES_TRADE_FEES: &str = "/api/v1/trade-fees";
pub(super) const FUTURES_POSITIONS: &str = "/api/v1/positions";
pub(super) const FUTURES_POSITION: &str = "/api/v2/position";
pub(super) const FUTURES_POSITION_MODE: &str = "/api/v2/position/getPositionMode";
pub(super) const FUTURES_CROSS_MARGIN_LEVERAGE: &str = "/api/v2/getCrossUserLeverage";
pub(super) const FUTURES_MODIFY_CROSS_MARGIN_LEVERAGE: &str = "/api/v2/changeCrossUserLeverage";

pub(super) const FUTURES_PLACE_ORDER: &str = "/api/v1/orders";
pub(super) const FUTURES_ORDER_LIST: &str = "/api/v1/orders";
pub(super) const FUTURES_ORDER: &str = "/api/v1/orders/{orderId}";
pub(super) const FUTURES_ORDER_BY_CLIENT_OID: &str = "/api/v1/orders/byClientOid";
pub(super) const FUTURES_CANCEL_ORDER: &str = "/api/v1/orders/{orderId}";
pub(super) const FUTURES_CANCEL_ORDER_BY_CLIENT_OID: &str =
    "/api/v1/orders/client-order/{clientOid}";
pub(super) const FUTURES_CANCEL_ALL_ORDERS: &str = "/api/v3/orders";
pub(super) const FUTURES_OPEN_ORDER_VALUE: &str = "/api/v1/openOrderStatistics";
pub(super) const FUTURES_TRADE_HISTORY: &str = "/api/v1/fills";
pub(super) const FUTURES_RECENT_TRADE_HISTORY: &str = "/api/v1/recentFills";
