//! Offline route coverage for every KuCoin dispatch name.
//!
//! Each case sends one request through `public_request` / `private_request`
//! against a local one-shot HTTP server and asserts the HTTP method, the REST
//! path from the official KuCoin API docs, and which base URL (spot or
//! futures) received the request. The other base URL points at a closed port,
//! so a request routed to the wrong host fails the test.

use std::time::Duration;
use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

use super::super::*;

const CLOSED_PORT: &str = "http://127.0.0.1:9";

#[derive(Clone, Copy)]
enum Host {
    Spot,
    Futures,
}

struct Case {
    name: &'static str,
    private: bool,
    host: Host,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
}

const fn public(
    name: &'static str,
    host: Host,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
) -> Case {
    Case {
        name,
        private: false,
        host,
        params,
        route,
    }
}

const fn private(
    name: &'static str,
    host: Host,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
) -> Case {
    Case {
        name,
        private: true,
        host,
        params,
        route,
    }
}

const SPOT: &str = "BTC-USDT-SPOT";
const SWAP: &str = "BTC-USDT-SWAP";

const PUBLIC_CASES: &[Case] = &[
    public(
        "get_currencies_v3",
        Host::Spot,
        &[],
        "GET /api/v3/currencies",
    ),
    public(
        "get_uta_oes_currency",
        Host::Spot,
        &[],
        "GET /api/ua/v2/oes/currency",
    ),
    public(
        "get_spot_24h_statistics",
        Host::Spot,
        &[("symbol", "BTC-USDT")],
        "GET /api/v1/market/stats?symbol=BTC-USDT",
    ),
    public(
        "get_client_ip_address",
        Host::Spot,
        &[],
        "GET /api/v1/my-ip",
    ),
    public(
        "get_kyc_regions",
        Host::Spot,
        &[],
        "GET /api/kyc/regions/v4",
    ),
    public(
        "get_spot_index_price",
        Host::Futures,
        &[("symbol", "BTC-USDT")],
        "GET /api/v1/index/query?symbol=BTC-USDT",
    ),
    public(
        "get_convert_currencies",
        Host::Spot,
        &[],
        "GET /api/v1/convert/currencies",
    ),
    public(
        "get_convert_symbol",
        Host::Spot,
        &[("fromCurrency", "BTC"), ("toCurrency", "USDT")],
        "GET /api/v1/convert/symbol?fromCurrency=BTC&toCurrency=USDT",
    ),
    public(
        "get_futures_interest_rate_index",
        Host::Futures,
        &[("symbol", ".XBTINT8H")],
        "GET /api/v1/interest/query?symbol=.XBTINT8H",
    ),
    public(
        "get_futures_premium_index",
        Host::Futures,
        &[("symbol", ".XBTUSDTMPI8H")],
        "GET /api/v1/premium/query?symbol=.XBTUSDTMPI8H",
    ),
    public(
        "get_margin_config",
        Host::Spot,
        &[],
        "GET /api/v1/margin/config",
    ),
    public(
        "get_announcements",
        Host::Spot,
        &[],
        "GET /api/v3/announcements",
    ),
    public(
        "get_call_auction_info",
        Host::Spot,
        &[("symbol", "BTC-USDT")],
        "GET /api/v1/market/callauctionData?symbol=BTC-USDT",
    ),
    public(
        "get_call_auction_part_order_book",
        Host::Spot,
        &[("size", "20"), ("symbol", "BTC-USDT")],
        "GET /api/v1/market/orderbook/callauction/level2_20?symbol=BTC-USDT",
    ),
    public(
        "get_spot_currency_v3",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/currencies/USDT",
    ),
    public("get_fiat_price", Host::Spot, &[], "GET /api/v1/prices"),
    public("get_market_list", Host::Spot, &[], "GET /api/v1/markets"),
    public(
        "get_spot_symbol_v2",
        Host::Spot,
        &[("symbol", "BTC-USDT")],
        "GET /api/v2/symbols/BTC-USDT",
    ),
    public(
        "get_uta_currencies",
        Host::Spot,
        &[],
        "GET /api/ua/v2/asset/currencies",
    ),
    public(
        "get_uta_currency",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/ua/v2/market/currency?currency=USDT",
    ),
    public(
        "get_uta_fiat_price",
        Host::Spot,
        &[("base", "USD")],
        "GET /api/ua/v2/market/fiat-price?base=USD",
    ),
    public(
        "get_uta_announcements",
        Host::Spot,
        &[],
        "GET /api/ua/v2/market/announcement",
    ),
    public(
        "get_uta_call_auction_info",
        Host::Spot,
        &[("symbol", "BTC-USDT")],
        "GET /api/ua/v2/market/call-auction-info?symbol=BTC-USDT",
    ),
    public(
        "get_uta_client_ip_address",
        Host::Spot,
        &[],
        "GET /api/ua/v2/user/my-ip",
    ),
    public(
        "get_uta_kyc_regions",
        Host::Spot,
        &[],
        "GET /api/ua/v2/user/kyc-region",
    ),
    public(
        "get_futures_all_tickers",
        Host::Futures,
        &[],
        "GET /api/v1/allTickers",
    ),
    public(
        "get_futures_mark_price",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/mark-price/XBTUSDTM/current",
    ),
    public(
        "get_futures_server_time",
        Host::Futures,
        &[],
        "GET /api/v1/timestamp",
    ),
    public(
        "get_futures_service_status",
        Host::Futures,
        &[],
        "GET /api/v1/status",
    ),
    public(
        "get_margin_mark_price",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v1/mark-price/BTC-USDT/current",
    ),
    public(
        "get_margin_mark_prices",
        Host::Spot,
        &[],
        "GET /api/v3/mark-price/all-symbols",
    ),
    public(
        "get_spot_server_time",
        Host::Spot,
        &[],
        "GET /api/v1/timestamp",
    ),
    public(
        "get_spot_service_status",
        Host::Spot,
        &[],
        "GET /api/v1/status",
    ),
    public(
        "get_uta_borrowable_currencies",
        Host::Spot,
        &[],
        "GET /api/ua/v2/market/borrowable-currency",
    ),
    public(
        "get_uta_collateral_ratios",
        Host::Spot,
        &[],
        "GET /api/ua/v2/market/collateral-discount-ratio",
    ),
    public(
        "get_uta_current_funding_rates",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/ua/v2/market/funding-rate?symbol=XBTUSDTM",
    ),
    public(
        "get_uta_funding_rate_history",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("startAt", "1700000000000"),
            ("endAt", "1700000060000"),
        ],
        "GET /api/ua/v2/market/funding-rate-history?symbol=XBTUSDTM&startAt=1700000000000&endAt=1700000060000",
    ),
    public(
        "get_uta_index_prices",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/ua/v2/market/index-price?symbol=XBTUSDTM",
    ),
    public(
        "get_uta_interest_rate_index",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/ua/v2/market/interest-rate-index?symbol=XBTUSDTM",
    ),
    public(
        "get_uta_klines",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "SPOT"),
            ("interval", "1min"),
        ],
        "GET /api/ua/v2/market/kline?symbol=BTC-USDT&tradeType=SPOT&interval=1min",
    ),
    public(
        "get_uta_service_status",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/server/status?tradeType=SPOT",
    ),
    public(
        "get_uta_tickers",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/market/ticker?tradeType=SPOT",
    ),
    public(
        "get_uta_trade_statistics",
        Host::Spot,
        &[],
        "GET /api/ua/v2/trade-statistics",
    ),
    public(
        "get_uta_public_trades",
        Host::Spot,
        &[("tradeType", "SPOT"), ("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/ua/v2/market/trade?tradeType=SPOT&symbol=BTC-USDT",
    ),
    public(
        "get_uta_instruments",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/market/instrument?tradeType=SPOT",
    ),
    public(
        "get_futures_current_funding_rate",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/funding-rate/XBTUSDTM/current",
    ),
    public(
        "get_futures_public_funding_history",
        Host::Futures,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("from", "1700000000000"),
            ("to", "1700000060000"),
        ],
        "GET /api/v1/contract/funding-rates?from=1700000000000&to=1700000060000&symbol=XBTUSDTM",
    ),
    public(
        "get_spot_instrument_info",
        Host::Spot,
        &[],
        "GET /api/v2/symbols",
    ),
    public(
        "get_spot_ticker",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/market/orderbook/level1?symbol=BTC-USDT",
    ),
    public(
        "get_spot_all_tickers",
        Host::Spot,
        &[],
        "GET /api/v1/market/allTickers",
    ),
    public(
        "get_spot_orderbook",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/market/orderbook/level2_20?symbol=BTC-USDT",
    ),
    public(
        "get_spot_public_trades",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/market/histories?symbol=BTC-USDT",
    ),
    public(
        "get_spot_kline",
        Host::Spot,
        &[("product_symbol", SPOT), ("timeframe", "1m")],
        "GET /api/v1/market/candles",
    ),
    public(
        "get_futures_contracts",
        Host::Futures,
        &[],
        "GET /api/v1/contracts/active",
    ),
    public(
        "get_futures_contract",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/contracts/XBTUSDTM",
    ),
    public(
        "get_futures_ticker",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/ticker?symbol=XBTUSDTM",
    ),
    public(
        "get_futures_orderbook",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/level2/snapshot?symbol=XBTUSDTM",
    ),
    public(
        "get_futures_orderbook",
        Host::Futures,
        &[("product_symbol", SWAP), ("depth", "20")],
        "GET /api/v1/level2/depth20?symbol=XBTUSDTM",
    ),
    public(
        "get_futures_public_trades",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/trade/history?symbol=XBTUSDTM",
    ),
    public(
        "get_futures_kline",
        Host::Futures,
        &[("product_symbol", SWAP), ("timeframe", "1m")],
        "GET /api/v1/kline/query",
    ),
    public(
        "get_futures_open_interest",
        Host::Spot,
        &[("product_symbol", SWAP)],
        "GET /api/ua/v2/market/open-interest?symbol=XBTUSDTM",
    ),
    public(
        "get_uta_position_tiers",
        Host::Spot,
        &[
            ("product_symbol", SWAP),
            ("tradeType", "FUTURES"),
            ("marginMode", "CROSS"),
            ("data", "RISK_LIMIT"),
            ("accountType", "UNIFIED"),
        ],
        "GET /api/ua/v2/market/position-tiers",
    ),
    public(
        "get_cross_margin_symbols",
        Host::Spot,
        &[],
        "GET /api/v3/margin/symbols",
    ),
    public(
        "get_isolated_margin_symbols",
        Host::Spot,
        &[],
        "GET /api/v1/isolated/symbols",
    ),
    public(
        "get_margin_collateral_ratio",
        Host::Spot,
        &[],
        "GET /api/v3/margin/collateralRatio",
    ),
    public(
        "get_margin_available_inventory",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/margin/available-inventory?currency=USDT",
    ),
    public(
        "get_margin_loan_market_interest_rate",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/project/marketInterestRate?currency=USDT",
    ),
];

const PRIVATE_CASES: &[Case] = &[
    private(
        "get_futures_24h_statistics",
        Host::Futures,
        &[],
        "GET /api/v1/trade-statistics",
    ),
    // Cases retained from the independent Python endpoint wire suite.
    private(
        "create_withdrawal",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("amount", "1.000000000000000001"),
            ("toAddress", "offline-address"),
            ("withdrawType", "ADDRESS"),
        ],
        "POST /api/v3/withdrawals",
    ),
    private(
        "create_uta_withdrawal",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("amount", "3"),
            ("toAddress", "123456"),
            ("withdrawType", "UID"),
        ],
        "POST /api/ua/v2/asset/withdrawal",
    ),
    private(
        "cancel_withdrawal",
        Host::Spot,
        &[("withdrawalId", "test-withdrawal")],
        "DELETE /api/v1/withdrawals/test-withdrawal",
    ),
    private(
        "cancel_uta_withdrawal",
        Host::Spot,
        &[("withdrawId", "test-withdrawal")],
        "POST /api/ua/v2/asset/withdraw/cancel",
    ),
    private(
        "cancel_margin_stop_order_by_id_raw",
        Host::Spot,
        &[("orderId", "test-order"), ("callerFlag", "keep")],
        "DELETE /api/v3/hf/margin/stop-order/cancel-by-id?orderId=test-order&callerFlag=keep",
    ),
    private(
        "set_uta_account_mode",
        Host::Spot,
        &[("accountType", "UNIFIED"), ("confirm", "true")],
        "POST /api/ua/v2/account/mode",
    ),
    private(
        "get_withdrawal_history_by_id",
        Host::Spot,
        &[("withdrawalId", "example")],
        "GET /api/v1/withdrawals/example",
    ),
    private(
        "get_withdrawal_history",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v1/withdrawals?currency=USDT",
    ),
    private(
        "get_withdrawal_quotas",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v1/withdrawals/quotas?currency=USDT",
    ),
    private(
        "get_loan_info",
        Host::Spot,
        &[],
        "GET /api/v1/otc-loan/loan",
    ),
    private(
        "get_otc_loan_accounts",
        Host::Spot,
        &[],
        "GET /api/v1/otc-loan/accounts",
    ),
    private(
        "get_discount_rate_configs",
        Host::Spot,
        &[],
        "GET /api/v1/otc-loan/discount-rate-configs",
    ),
    private(
        "get_uta_oes_custody_quota",
        Host::Spot,
        &[],
        "GET /api/ua/v2/oes/custody-quota",
    ),
    private(
        "get_uta_accounts",
        Host::Spot,
        &[],
        "GET /api/ua/v2/otc-loan/account",
    ),
    private(
        "get_uta_discount_rate_configs",
        Host::Spot,
        &[],
        "GET /api/ua/v2/otc-loan/discount-rate",
    ),
    private(
        "get_uta_loan_info",
        Host::Spot,
        &[],
        "GET /api/ua/v2/otc-loan/loan",
    ),
    private(
        "get_uta_withdrawal_history",
        Host::Spot,
        &[],
        "GET /api/ua/v2/asset/withdrawal/history",
    ),
    private(
        "get_uta_withdrawal_quotas",
        Host::Spot,
        &[("currency", "USDT"), ("withdrawType", "ADDRESS")],
        "GET /api/ua/v2/withdrawals/quotas?currency=USDT&withdrawType=ADDRESS",
    ),
    private("get_account_info", Host::Spot, &[], "GET /api/v2/user-info"),
    private(
        "get_spot_account_type",
        Host::Spot,
        &[],
        "GET /api/v1/hf/accounts/opened",
    ),
    private(
        "add_sub_account",
        Host::Spot,
        &[
            ("password", "trade1234"),
            ("subName", "trader123"),
            ("access", "Spot"),
        ],
        "POST /api/v2/sub/user/created",
    ),
    private(
        "get_apikey_info",
        Host::Spot,
        &[],
        "GET /api/v1/user/api-key",
    ),
    private(
        "create_deposit_address_v3",
        Host::Spot,
        &[("currency", "USDT"), ("chain", "trx")],
        "POST /api/v3/deposit-address/create",
    ),
    private(
        "get_deposit_addresses_v3",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/deposit-addresses?currency=USDT",
    ),
    private(
        "add_sub_account_api",
        Host::Spot,
        &[
            ("passphrase", "testpass123"),
            ("remark", "trading"),
            ("subName", "trader123"),
        ],
        "POST /api/v1/sub/api-key",
    ),
    private(
        "delete_sub_account_api",
        Host::Spot,
        &[
            ("apiKey", "query-key"),
            ("subName", "trader123"),
            ("passphrase", "testpass123"),
        ],
        "DELETE /api/v1/sub/api-key?apiKey=query-key&subName=trader123&passphrase=testpass123",
    ),
    private(
        "get_sub_account_api_list",
        Host::Spot,
        &[("subName", "trader123")],
        "GET /api/v1/sub/api-key?subName=trader123",
    ),
    private(
        "modify_sub_account_api",
        Host::Spot,
        &[
            ("passphrase", "testpass123"),
            ("subName", "trader123"),
            ("apiKey", "query-key"),
        ],
        "POST /api/v1/sub/api-key/update",
    ),
    private(
        "add_sub_account_futures_permission",
        Host::Spot,
        &[("uid", "123")],
        "POST /api/v3/sub/user/futures/enable",
    ),
    private(
        "add_sub_account_margin_permission",
        Host::Spot,
        &[("uid", "123")],
        "POST /api/v3/sub/user/margin/enable",
    ),
    private("get_basic_fee", Host::Spot, &[], "GET /api/v1/base-fee"),
    private(
        "add_convert_limit_order",
        Host::Spot,
        &[
            ("clientOrderId", "client-order-1"),
            ("fromCurrency", "BTC"),
            ("toCurrency", "USDT"),
            ("fromCurrencySize", "0.123456789123456789"),
            ("toCurrencySize", "1000.123456789123456789"),
        ],
        "POST /api/v1/convert/limit/order",
    ),
    private(
        "add_convert_order",
        Host::Spot,
        &[("clientOrderId", "client-order-1"), ("quoteId", "quote-1")],
        "POST /api/v1/convert/order",
    ),
    private(
        "cancel_convert_limit_order",
        Host::Spot,
        &[("orderId", "order-1")],
        "DELETE /api/v1/convert/limit/order/cancel?orderId=order-1",
    ),
    private(
        "get_convert_limit_order_detail",
        Host::Spot,
        &[("orderId", "order-1")],
        "GET /api/v1/convert/limit/order/detail?orderId=order-1",
    ),
    private(
        "get_convert_limit_order_detail_list",
        Host::Spot,
        &[],
        "GET /api/v1/convert/limit/orders",
    ),
    private(
        "get_convert_limit_quote",
        Host::Spot,
        &[
            ("fromCurrency", "BTC"),
            ("toCurrency", "USDT"),
            ("fromCurrencySize", "0.123456789123456789"),
        ],
        "GET /api/v1/convert/limit/quote?fromCurrency=BTC&toCurrency=USDT&fromCurrencySize=0.123456789123456789",
    ),
    private(
        "get_convert_order_detail",
        Host::Spot,
        &[("orderId", "order-1")],
        "GET /api/v1/convert/order/detail?orderId=order-1",
    ),
    private(
        "get_convert_order_history",
        Host::Spot,
        &[],
        "GET /api/v1/convert/order/history",
    ),
    private(
        "get_convert_quote",
        Host::Spot,
        &[
            ("fromCurrency", "BTC"),
            ("toCurrency", "USDT"),
            ("fromCurrencySize", "0.123456789123456789"),
        ],
        "GET /api/v1/convert/quote?fromCurrency=BTC&toCurrency=USDT&fromCurrencySize=0.123456789123456789",
    ),
    private(
        "add_uta_sub_account",
        Host::Spot,
        &[
            ("password", "trade1234"),
            ("subName", "trader123"),
            ("access", "Spot"),
        ],
        "POST /api/ua/v2/user/sub/create-sub-account",
    ),
    private(
        "add_uta_sub_account_api",
        Host::Spot,
        &[
            ("subName", "trader123"),
            ("passphrase", "testpass123"),
            ("remark", "trading"),
        ],
        "POST /api/ua/v2/user/create-sub-api-key",
    ),
    private(
        "get_uta_apikey_info",
        Host::Spot,
        &[],
        "GET /api/ua/v2/user/api-key",
    ),
    private(
        "delete_uta_sub_account_api",
        Host::Spot,
        &[
            ("apiKey", "query-key"),
            ("subName", "trader123"),
            ("passphrase", "testpass123"),
        ],
        "DELETE /api/ua/v2/user/sub-api-key?apiKey=query-key&subName=trader123&passphrase=testpass123",
    ),
    private(
        "get_uta_deposit_address",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/ua/v2/asset/deposit/address?currency=USDT",
    ),
    private(
        "get_uta_deposit_history",
        Host::Spot,
        &[],
        "GET /api/ua/v2/asset/deposit/history",
    ),
    private(
        "set_uta_kcs_fee_deduction",
        Host::Spot,
        &[("enabled", "true")],
        "GET /api/ua/v2/account/fee/kcs-deduct?enabled=true",
    ),
    private(
        "modify_uta_sub_account_api",
        Host::Spot,
        &[
            ("subName", "trader123"),
            ("apiKey", "query-key"),
            ("passphrase", "testpass123"),
        ],
        "POST /api/ua/v2/user/modify-sub-api-key",
    ),
    private(
        "set_uta_rate_limit",
        Host::Spot,
        &[("list", "[{\"uid\":\"123\",\"rate\":50}]")],
        "POST /api/ua/v2/rate-limit/set",
    ),
    private(
        "get_uta_sub_account_api_list",
        Host::Spot,
        &[("apiKey", "query-key"), ("subName", "trader123")],
        "GET /api/ua/v2/user/sub-api-key?apiKey=query-key&subName=trader123",
    ),
    private(
        "set_uta_sub_account_transfer_permission",
        Host::Spot,
        &[("subUids", "123"), ("subToSub", "true")],
        "POST /api/ua/v2/sub-account/canTransferOut",
    ),
    private(
        "place_spot_order_sync",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("side", "buy"),
            ("type", "limit"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/hf/orders/sync",
    ),
    private(
        "place_spot_batch_orders_sync",
        Host::Spot,
        &[(
            "orders",
            r#"[{"symbol":"BTC-USDT","side":"buy","type":"market","funds":"10"}]"#,
        )],
        "POST /api/v1/hf/orders/multi/sync",
    ),
    private(
        "cancel_spot_order_sync",
        Host::Spot,
        &[("product_symbol", SPOT), ("orderId", "order-1")],
        "DELETE /api/v1/hf/orders/sync/order-1?symbol=BTC-USDT",
    ),
    private(
        "cancel_spot_order_by_client_oid_sync",
        Host::Spot,
        &[("product_symbol", SPOT), ("clientOid", "sync-1")],
        "DELETE /api/v1/hf/orders/sync/client-order/sync-1?symbol=BTC-USDT",
    ),
    private(
        "get_futures_account_ledgers",
        Host::Futures,
        &[],
        "GET /api/v1/transaction-history",
    ),
    private(
        "get_margin_hf_account_ledgers",
        Host::Spot,
        &[],
        "GET /api/v3/hf/margin/account/ledgers",
    ),
    private(
        "get_spot_account_ledgers",
        Host::Spot,
        &[],
        "GET /api/v1/accounts/ledgers",
    ),
    private(
        "get_spot_hf_account_ledgers",
        Host::Spot,
        &[],
        "GET /api/v1/hf/accounts/ledgers",
    ),
    private(
        "get_deposit_history",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v1/deposits?currency=USDT",
    ),
    private(
        "get_margin_currency_risk_limits",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/margin/currencies?currency=USDT",
    ),
    private(
        "get_spot_full_orderbook",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v3/market/orderbook/level2?symbol=BTC-USDT",
    ),
    private(
        "get_uta_account_ledgers",
        Host::Spot,
        &[("accountType", "UNIFIED")],
        "GET /api/ua/v2/account/ledger?accountType=UNIFIED",
    ),
    private(
        "get_classic_account_balances_v2",
        Host::Spot,
        &[("accountType", "SPOT")],
        "GET /api/ua/v2/account/balance?accountType=SPOT",
    ),
    private(
        "transfer_uta_accounts",
        Host::Spot,
        &[
            ("clientOid", "transfer-123"),
            ("transferType", "INTERNAL"),
            ("currency", "USDT"),
            ("amount", "1"),
            ("fromAccountType", "FUNDING"),
            ("fromAccountTag", "DEFAULT"),
            ("toAccountType", "SPOT"),
            ("toAccountTag", "DEFAULT"),
        ],
        "POST /api/ua/v2/account/transfer",
    ),
    private(
        "get_uta_account_mode",
        Host::Spot,
        &[],
        "GET /api/ua/v2/account/mode",
    ),
    private(
        "get_uta_all_rate_limits",
        Host::Spot,
        &[],
        "GET /api/ua/v2/rate-limit/query-all",
    ),
    private(
        "get_uta_rate_limits",
        Host::Spot,
        &[("uids", "123,456")],
        "GET /api/ua/v2/rate-limit/query?uids=123%2C456",
    ),
    private(
        "get_uta_rate_limit_cap",
        Host::Spot,
        &[],
        "GET /api/ua/v2/rate-limit/query-cap",
    ),
    private(
        "get_uta_borrowing_rates_limits",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/ua/v2/account/interest-limits?currency=USDT",
    ),
    private(
        "get_uta_interest_history",
        Host::Spot,
        &[("accountType", "UNIFIED")],
        "GET /api/ua/v2/account/interest-history?accountType=UNIFIED",
    ),
    private(
        "get_uta_orderbook",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("limit", "FULL"),
        ],
        "GET /api/ua/v2/market/orderbook?tradeType=SPOT&symbol=BTC-USDT&limit=FULL",
    ),
    private(
        "get_uta_transfer_quota",
        Host::Spot,
        &[("accountType", "UNIFIED"), ("currency", "USDT")],
        "GET /api/ua/v2/account/transfer-quota?accountType=UNIFIED&currency=USDT",
    ),
    private(
        "place_futures_batch_orders",
        Host::Futures,
        &[(
            "orders",
            r#"[{"clientOid": "batch-1", "product_symbol": "BTC-USDT-SWAP", "side": "buy", "type": "limit", "size": 1, "price": "100", "leverage": 3}]"#,
        )],
        "POST /api/v1/orders/multi",
    ),
    private(
        "cancel_futures_batch_orders",
        Host::Futures,
        &[("orderIdsList", r#"["1","2"]"#)],
        "DELETE /api/v1/orders/multi-cancel",
    ),
    private(
        "set_futures_batch_margin_mode",
        Host::Futures,
        &[("marginMode", "CROSS"), ("symbols", r#"["BTC-USDT-SWAP"]"#)],
        "POST /api/v2/position/batchChangeMarginMode",
    ),
    private(
        "get_spot_stop_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "c-1")],
        "GET /api/v1/stop-order/queryOrderByClientOid?clientOid=c-1",
    ),
    private(
        "cancel_spot_order_by_client_oid",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("clientOid", "test-order-1"),
        ],
        "DELETE /api/v1/hf/orders/client-order/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "cancel_spot_partial_order",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("cancelSize", "1"),
            ("orderId", "test-order-1"),
        ],
        "DELETE /api/v1/hf/orders/cancel/test-order-1?cancelSize=1&symbol=BTC-USDT",
    ),
    private(
        "get_spot_order",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("orderId", "test-order-1"),
        ],
        "GET /api/v1/hf/orders/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "get_spot_order_by_client_oid",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("clientOid", "test-order-1"),
        ],
        "GET /api/v1/hf/orders/client-order/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "get_spot_active_order_symbols",
        Host::Spot,
        &[],
        "GET /api/v1/hf/orders/active/symbols",
    ),
    private(
        "get_spot_active_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v1/hf/orders/active?symbol=BTC-USDT",
    ),
    private(
        "get_spot_closed_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v1/hf/orders/done?symbol=BTC-USDT",
    ),
    private(
        "place_spot_stop_order",
        Host::Spot,
        &[
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("type", "limit"),
            ("price", "100"),
            ("size", "1"),
            ("stopPrice", "100"),
        ],
        "POST /api/v1/stop-order",
    ),
    private(
        "cancel_spot_stop_order_by_client_oid",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("clientOid", "test-order-1"),
        ],
        "DELETE /api/v1/stop-order/cancelOrderByClientOid?clientOid=test-order-1&symbol=BTC-USDT",
    ),
    private(
        "cancel_spot_stop_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "DELETE /api/v1/stop-order/test-order-1",
    ),
    private(
        "cancel_spot_stop_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "DELETE /api/v1/stop-order/cancel?symbol=BTC-USDT",
    ),
    private(
        "get_spot_stop_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v1/stop-order?symbol=BTC-USDT",
    ),
    private(
        "get_spot_stop_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v1/stop-order/test-order-1",
    ),
    private(
        "place_spot_oco_order",
        Host::Spot,
        &[
            ("clientOid", "test-order-1"),
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("price", "100"),
            ("size", "1"),
            ("stopPrice", "100"),
            ("limitPrice", "100"),
        ],
        "POST /api/v3/oco/order",
    ),
    private(
        "cancel_spot_oco_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "DELETE /api/v3/oco/order/test-order-1",
    ),
    private(
        "cancel_spot_oco_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "DELETE /api/v3/oco/client-order/test-order-1",
    ),
    private(
        "cancel_spot_oco_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "DELETE /api/v3/oco/orders?symbol=BTC-USDT",
    ),
    private(
        "get_spot_oco_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v3/oco/order/test-order-1",
    ),
    private(
        "get_spot_oco_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "GET /api/v3/oco/client-order/test-order-1",
    ),
    private(
        "get_spot_oco_order_details",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v3/oco/order/details/test-order-1",
    ),
    private(
        "get_spot_oco_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v3/oco/orders?symbol=BTC-USDT",
    ),
    private(
        "place_margin_order",
        Host::Spot,
        &[
            ("clientOid", "test-order-1"),
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("type", "limit"),
            ("price", "100"),
            ("size", "1"),
        ],
        "POST /api/v3/hf/margin/order",
    ),
    private(
        "test_margin_order",
        Host::Spot,
        &[
            ("clientOid", "test-order-1"),
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("type", "limit"),
            ("price", "100"),
            ("size", "1"),
        ],
        "POST /api/v3/hf/margin/order/test",
    ),
    private(
        "cancel_margin_order",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("orderId", "test-order-1"),
        ],
        "DELETE /api/v3/hf/margin/orders/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "cancel_margin_order_by_client_oid",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("clientOid", "test-order-1"),
        ],
        "DELETE /api/v3/hf/margin/orders/client-order/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "cancel_margin_orders_by_symbol",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "MARGIN_TRADE"),
        ],
        "DELETE /api/v3/hf/margin/orders?tradeType=MARGIN_TRADE&symbol=BTC-USDT",
    ),
    private(
        "get_margin_active_order_symbols",
        Host::Spot,
        &[("tradeType", "MARGIN_TRADE")],
        "GET /api/v3/hf/margin/order/active/symbols?tradeType=MARGIN_TRADE",
    ),
    private(
        "get_margin_open_orders",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "MARGIN_TRADE"),
        ],
        "GET /api/v3/hf/margin/orders/active?tradeType=MARGIN_TRADE&symbol=BTC-USDT",
    ),
    private(
        "get_margin_closed_orders",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "MARGIN_TRADE"),
        ],
        "GET /api/v3/hf/margin/orders/done?tradeType=MARGIN_TRADE&symbol=BTC-USDT",
    ),
    private(
        "get_margin_trade_history",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "MARGIN_TRADE"),
        ],
        "GET /api/v3/hf/margin/fills?tradeType=MARGIN_TRADE&symbol=BTC-USDT",
    ),
    private(
        "get_margin_order",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("orderId", "test-order-1"),
        ],
        "GET /api/v3/hf/margin/orders/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "get_margin_order_by_client_oid",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("clientOid", "test-order-1"),
        ],
        "GET /api/v3/hf/margin/orders/client-order/test-order-1?symbol=BTC-USDT",
    ),
    private(
        "place_margin_stop_order",
        Host::Spot,
        &[
            ("clientOid", "test-order-1"),
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("type", "limit"),
            ("price", "100"),
            ("size", "1"),
            ("isIsolated", "false"),
            ("autoBorrow", "false"),
            ("autoRepay", "false"),
            ("stopPrice", "100"),
        ],
        "POST /api/v3/hf/margin/stop-order",
    ),
    private(
        "cancel_margin_stop_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "DELETE /api/v3/hf/margin/stop-order/cancel-by-clientOid?clientOid=test-order-1",
    ),
    private(
        "cancel_margin_stop_orders",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("tradeType", "MARGIN_TRADE"),
        ],
        "DELETE /api/v3/hf/margin/stop-order/cancel?tradeType=MARGIN_TRADE&symbol=BTC-USDT",
    ),
    private(
        "get_margin_stop_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET /api/v3/hf/margin/stop-orders?symbol=BTC-USDT",
    ),
    private(
        "get_margin_stop_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v3/hf/margin/stop-order/orderId?orderId=test-order-1",
    ),
    private(
        "get_margin_stop_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "GET /api/v3/hf/margin/stop-order/clientOid?clientOid=test-order-1",
    ),
    private(
        "place_margin_oco_order",
        Host::Spot,
        &[
            ("clientOid", "test-order-1"),
            ("side", "buy"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("price", "100"),
            ("size", "1"),
            ("stopPrice", "100"),
            ("limitPrice", "100"),
            ("isIsolated", "false"),
        ],
        "POST /api/v3/hf/margin/oco-order",
    ),
    private(
        "cancel_margin_oco_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "DELETE /api/v3/hf/margin/oco-order/cancel-by-id?orderId=test-order-1",
    ),
    private(
        "cancel_margin_oco_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "DELETE /api/v3/hf/margin/oco-order/cancel-by-clientOid?clientOid=test-order-1",
    ),
    private(
        "cancel_margin_oco_orders",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SPOT")],
        "DELETE /api/v3/hf/margin/oco-order/cancel?symbol=BTC-USDT",
    ),
    private(
        "get_margin_oco_order",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v3/hf/margin/oco-order/orderId?orderId=test-order-1",
    ),
    private(
        "get_margin_oco_order_by_client_oid",
        Host::Spot,
        &[("clientOid", "test-order-1")],
        "GET /api/v3/hf/margin/oco-order/clientOid?clientOid=test-order-1",
    ),
    private(
        "get_margin_oco_order_details",
        Host::Spot,
        &[("orderId", "test-order-1")],
        "GET /api/v3/hf/margin/oco-order/detail/orderId?orderId=test-order-1",
    ),
    private(
        "get_margin_oco_orders",
        Host::Spot,
        &[
            ("pageSize", "20"),
            ("currentPage", "1"),
            ("product_symbol", "BTC-USDT-SPOT"),
        ],
        "GET /api/v3/hf/margin/oco-orders?pageSize=20&currentPage=1&symbol=BTC-USDT",
    ),
    private(
        "place_futures_tpsl_order",
        Host::Futures,
        &[
            ("side", "buy"),
            ("clientOid", "test-order-1"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("type", "limit"),
            ("stopPriceType", "MP"),
            ("price", "100"),
            ("size", "1"),
            ("triggerStopDownPrice", "100"),
        ],
        "POST /api/v1/st-orders",
    ),
    private(
        "cancel_futures_stop_orders",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "DELETE /api/v1/stopOrders?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_recent_closed_orders",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/recentDoneOrders?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_stop_orders",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/stopOrders?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_margin_mode",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v2/position/getMarginMode?symbol=XBTUSDTM",
    ),
    private(
        "set_futures_margin_mode",
        Host::Futures,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("marginMode", "ISOLATED"),
        ],
        "POST /api/v2/position/changeMarginMode",
    ),
    private(
        "set_futures_position_mode",
        Host::Futures,
        &[("positionMode", "0")],
        "POST /api/v2/position/switchPositionMode",
    ),
    private(
        "get_futures_max_open_size",
        Host::Futures,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("price", "100"),
            ("leverage", "1"),
        ],
        "GET /api/v2/getMaxOpenSize?price=100&leverage=1&symbol=XBTUSDTM",
    ),
    private(
        "get_futures_position_history",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/history-positions?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_max_withdraw_margin",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/margin/maxWithdrawMargin?symbol=XBTUSDTM",
    ),
    private(
        "add_futures_isolated_margin",
        Host::Futures,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("margin", "1.25"),
            ("bizNo", "test-order-1"),
        ],
        "POST /api/v1/position/margin/deposit-margin",
    ),
    private(
        "remove_futures_isolated_margin",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP"), ("withdrawAmount", "1")],
        "POST /api/v1/margin/withdrawMargin",
    ),
    private(
        "get_futures_cross_margin_risk_limit",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v2/batchGetCrossOrderLimit?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_cross_margin_requirement",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP"), ("positionValue", "1")],
        "POST /api/v2/getCrossModeMarginRequirement",
    ),
    private(
        "get_futures_isolated_margin_risk_limit",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/contracts/risk-limit/XBTUSDTM",
    ),
    private(
        "set_futures_isolated_margin_risk_limit",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP"), ("level", "1")],
        "POST /api/v1/position/risk-limit-level/change",
    ),
    private(
        "get_futures_funding_history",
        Host::Futures,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/v1/funding-history?symbol=XBTUSDTM",
    ),
    private(
        "batch_cancel_uta_orders",
        Host::Spot,
        &[
            ("tradeType", "FUTURES"),
            (
                "cancelOrderList",
                "[{\"symbol\": \"BTC-USDT-SWAP\", \"orderId\": \"1\", \"clientOid\": \"c\"}, {\"symbol\": \"ETHUSDTM\", \"clientOid\": \"d\"}]",
            ),
        ],
        "POST /api/ua/v2/unified/order/cancel-batch",
    ),
    private(
        "cancel_uta_orders_by_symbol",
        Host::Spot,
        &[
            ("tradeType", "FUTURES"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("orderFilter", "ADVANCED"),
            ("marginMode", "ISOLATED"),
        ],
        "POST /api/ua/v2/unified/order/cancel-all",
    ),
    private(
        "get_uta_margin_mode",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET /api/ua/v2/unified/position/margin-mode",
    ),
    private(
        "set_uta_margin_mode",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP"), ("marginMode", "CROSS")],
        "POST /api/ua/v2/unified/position/margin-mode",
    ),
    private(
        "modify_uta_position_margin",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("type", "WITHDRAW"),
            ("amount", "1.25"),
        ],
        "POST /api/ua/v2/unified/position/modify-margin",
    ),
    private(
        "get_uta_max_order_quantity",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", "BTC-USDT-SPOT"),
            ("price", "123.45"),
        ],
        "GET /api/ua/v2/order/max-order-quantity",
    ),
    private(
        "get_uta_leverage",
        Host::Spot,
        &[
            ("tradeType", "MARGIN"),
            ("currency", "USDT"),
            ("marginMode", "CROSS"),
        ],
        "GET /api/ua/v2/unified/account/leverage",
    ),
    private(
        "modify_uta_futures_leverage",
        Host::Spot,
        &[("product_symbol", "BTC-USDT-SWAP"), ("leverage", "3")],
        "POST /api/ua/v2/unified/account/modify-leverage",
    ),
    private(
        "modify_uta_cross_margin_leverage",
        Host::Spot,
        &[("leverage", "2"), ("currency", "USDT")],
        "POST /api/ua/v2/unified/account/modify-leverage-margin-cross",
    ),
    private(
        "get_uta_position_history",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("lastId", "1234"),
            ("pageSize", "20"),
        ],
        "GET /api/ua/v2/position/history",
    ),
    private(
        "get_uta_funding_history",
        Host::Spot,
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("startAt", "1700000000000"),
            ("endAt", "1700000060000"),
            ("lastId", "42"),
            ("pageSize", "200"),
        ],
        "GET /api/ua/v2/position/funding-history",
    ),
    // Account, fees, sub-accounts, transfers.
    private(
        "get_spot_fee_rates",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/trade-fees?symbols=BTC-USDT",
    ),
    private(
        "get_futures_fee_rates",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/trade-fees?symbol=XBTUSDTM",
    ),
    private(
        "get_uta_fee_rates",
        Host::Spot,
        &[("tradeType", "SPOT"), ("symbol", "BTC-USDT")],
        "GET /api/ua/v2/user/fee-rate",
    ),
    private(
        "get_account_balance",
        Host::Spot,
        &[("currency", "USDT"), ("type", "trade")],
        "GET /api/v1/accounts?currency=USDT&type=trade",
    ),
    private(
        "get_transfer_quotas",
        Host::Spot,
        &[("currency", "USDT"), ("account_type", "MAIN")],
        "GET /api/v1/accounts/transferable",
    ),
    private(
        "flex_transfer",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("amount", "1"),
            ("fromAccountType", "MAIN"),
            ("toAccountType", "TRADE"),
        ],
        "POST /api/v3/accounts/universal-transfer",
    ),
    private("get_subaccounts", Host::Spot, &[], "GET /api/v2/sub/user"),
    private(
        "get_spot_subaccount_balances",
        Host::Spot,
        &[],
        "GET /api/v2/sub-accounts",
    ),
    private(
        "get_uta_subaccounts",
        Host::Spot,
        &[],
        "GET /api/ua/v2/user/sub-account-list",
    ),
    private(
        "get_subaccount_balance",
        Host::Spot,
        &[("subUserId", "123")],
        "GET /api/v1/sub-accounts/123",
    ),
    private(
        "get_futures_subaccount_balances",
        Host::Futures,
        &[("currency", "USDT")],
        "GET /api/v1/account-overview-all?currency=USDT",
    ),
    private(
        "get_uta_subaccount_currency_assets",
        Host::Spot,
        &[],
        "GET /api/ua/v2/sub-account/balance",
    ),
    private(
        "get_futures_account",
        Host::Futures,
        &[("currency", "USDT")],
        "GET /api/v1/account-overview?currency=USDT",
    ),
    private(
        "get_futures_positions",
        Host::Futures,
        &[],
        "GET /api/v1/positions",
    ),
    private(
        "get_futures_position",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v2/position?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_position_mode",
        Host::Futures,
        &[],
        "GET /api/v2/position/getPositionMode",
    ),
    private(
        "get_futures_cross_margin_leverage",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v2/getCrossUserLeverage?symbol=XBTUSDTM",
    ),
    private(
        "modify_futures_cross_margin_leverage",
        Host::Futures,
        &[("product_symbol", SWAP), ("leverage", "5")],
        "POST /api/v2/changeCrossUserLeverage",
    ),
    // UTA (unified trading account).
    private(
        "get_uta_positions",
        Host::Spot,
        &[],
        "GET /api/ua/v2/unified/position/open-list",
    ),
    private(
        "get_uta_account_balance",
        Host::Spot,
        &[],
        "GET /api/ua/v2/unified/account/balance",
    ),
    private(
        "get_uta_account_overview",
        Host::Spot,
        &[],
        "GET /api/ua/v2/unified/account/overview",
    ),
    private(
        "place_uta_order",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", SPOT),
            ("side", "BUY"),
            ("orderType", "LIMIT"),
            ("size", "1"),
            ("sizeUnit", "BASECCY"),
            ("price", "100"),
        ],
        "POST /api/ua/v2/unified/order/place",
    ),
    private(
        "cancel_uta_order",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", SPOT),
            ("orderId", "1"),
        ],
        "POST /api/ua/v2/unified/order/cancel",
    ),
    private(
        "amend_uta_order",
        Host::Spot,
        &[
            ("product_symbol", SWAP),
            ("orderId", "1"),
            ("newPrice", "101"),
        ],
        "POST /api/ua/v2/unified/order/amend",
    ),
    private(
        "get_uta_order_detail",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", SPOT),
            ("orderId", "1"),
        ],
        "GET /api/ua/v2/unified/order/detail",
    ),
    private(
        "get_uta_open_orders",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/unified/order/open-list",
    ),
    private(
        "get_uta_order_history",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/unified/order/history",
    ),
    private(
        "get_uta_trade_history",
        Host::Spot,
        &[("tradeType", "SPOT")],
        "GET /api/ua/v2/unified/order/execution",
    ),
    // Earn.
    private(
        "purchase_earn",
        Host::Spot,
        &[
            ("productId", "1"),
            ("amount", "10"),
            ("accountType", "MAIN"),
        ],
        "POST /api/v1/earn/orders",
    ),
    private(
        "get_earn_redeem_preview",
        Host::Spot,
        &[("orderId", "1"), ("fromAccountType", "MAIN")],
        "GET /api/v1/earn/redeem-preview",
    ),
    private(
        "redeem_earn",
        Host::Spot,
        &[("orderId", "1"), ("amount", "10")],
        "DELETE /api/v1/earn/orders",
    ),
    private(
        "get_earn_savings_products",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v1/earn/saving/products?currency=USDT",
    ),
    private(
        "get_earn_promotion_products",
        Host::Spot,
        &[],
        "GET /api/v1/earn/promotion/products",
    ),
    private(
        "get_earn_staking_products",
        Host::Spot,
        &[],
        "GET /api/v1/earn/staking/products",
    ),
    private(
        "get_earn_kcs_staking_products",
        Host::Spot,
        &[],
        "GET /api/v1/earn/kcs-staking/products",
    ),
    private(
        "get_earn_eth_staking_products",
        Host::Spot,
        &[],
        "GET /api/v1/earn/eth-staking/products",
    ),
    private(
        "get_earn_account_holdings",
        Host::Spot,
        &[],
        "GET /api/v1/earn/hold-assets",
    ),
    private(
        "get_dual_investment_products",
        Host::Spot,
        &[
            ("category", "DUAL_CLASSIC"),
            ("strikeCurrency", "BTC"),
            ("investCurrency", "USDT"),
            ("side", "CALL"),
        ],
        "GET /api/v1/struct-earn/dual/products",
    ),
    private(
        "purchase_structured_earn",
        Host::Spot,
        &[
            ("productId", "1"),
            ("investCurrency", "USDT"),
            ("investAmount", "10"),
            ("accountType", "MAIN"),
        ],
        "POST /api/v1/struct-earn/orders",
    ),
    private(
        "get_structured_earn_orders",
        Host::Spot,
        &[("categories", "DUAL_CLASSIC")],
        "GET /api/v1/struct-earn/orders",
    ),
    // Margin.
    private(
        "get_cross_margin_account",
        Host::Spot,
        &[],
        "GET /api/v3/margin/accounts",
    ),
    private(
        "get_isolated_margin_account",
        Host::Spot,
        &[],
        "GET /api/v3/isolated/accounts",
    ),
    private(
        "get_margin_borrow_interest_rate",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/margin/borrowRate",
    ),
    private(
        "borrow_margin",
        Host::Spot,
        &[("currency", "USDT"), ("size", "10"), ("timeInForce", "IOC")],
        "POST /api/v3/margin/borrow",
    ),
    private(
        "get_margin_borrow_history",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/margin/borrow",
    ),
    private(
        "repay_margin",
        Host::Spot,
        &[("currency", "USDT"), ("size", "10")],
        "POST /api/v3/margin/repay",
    ),
    private(
        "get_margin_repay_history",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/margin/repay",
    ),
    private(
        "modify_margin_leverage",
        Host::Spot,
        &[("leverage", "3")],
        "POST /api/v3/position/update-user-leverage",
    ),
    private(
        "get_margin_loan_market",
        Host::Spot,
        &[("currency", "USDT")],
        "GET /api/v3/project/list",
    ),
    private(
        "purchase_margin_lending",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("size", "10"),
            ("interestRate", "0.01"),
        ],
        "POST /api/v3/purchase",
    ),
    private(
        "modify_margin_lending_purchase",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("purchaseOrderNo", "1"),
            ("interestRate", "0.01"),
        ],
        "POST /api/v3/lend/purchase/update",
    ),
    private(
        "get_margin_lending_purchase_orders",
        Host::Spot,
        &[("status", "DONE"), ("currency", "USDT")],
        "GET /api/v3/purchase/orders",
    ),
    private(
        "redeem_margin_lending",
        Host::Spot,
        &[
            ("currency", "USDT"),
            ("size", "10"),
            ("purchaseOrderNo", "1"),
        ],
        "POST /api/v3/redeem",
    ),
    private(
        "get_margin_lending_redeem_orders",
        Host::Spot,
        &[("status", "DONE"), ("currency", "USDT")],
        "GET /api/v3/redeem/orders",
    ),
    private(
        "get_margin_interest_history",
        Host::Spot,
        &[("currency", "USDT"), ("product_symbol", SPOT)],
        "GET /api/v3/margin/interest?currency=USDT&symbol=BTC-USDT",
    ),
    // Dead-man switch.
    private(
        "set_dcp",
        Host::Spot,
        &[("timeout", "10"), ("symbols", "BTC-USDT")],
        "POST /api/v1/hf/orders/dead-cancel-all",
    ),
    private(
        "get_dcp",
        Host::Spot,
        &[],
        "GET /api/v1/hf/orders/dead-cancel-all/query",
    ),
    // Spot HF orders.
    private(
        "place_spot_order",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("side", "buy"),
            ("type", "limit"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/hf/orders",
    ),
    private(
        "test_spot_order",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("side", "buy"),
            ("type", "limit"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/hf/orders/test",
    ),
    private(
        "place_spot_market_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("side", "buy"), ("size", "1")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_market_buy_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("funds", "10")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_market_sell_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("size", "1")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_limit_order",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("side", "sell"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_limit_buy_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("size", "1"), ("price", "100")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_limit_sell_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("size", "1"), ("price", "100")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_post_only_limit_order",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("side", "buy"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_post_only_limit_buy_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("size", "1"), ("price", "100")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_post_only_limit_sell_order",
        Host::Spot,
        &[("product_symbol", SPOT), ("size", "1"), ("price", "100")],
        "POST /api/v1/hf/orders",
    ),
    private(
        "place_spot_batch_orders",
        Host::Spot,
        &[(
            "orders",
            r#"[{"product_symbol":"BTC-USDT-SPOT","side":"buy","type":"limit","size":"1","price":"100"}]"#,
        )],
        "POST /api/v1/hf/orders/multi",
    ),
    private(
        "place_spot_batch_limit_orders",
        Host::Spot,
        &[(
            "orders",
            r#"[{"product_symbol":"BTC-USDT-SPOT","side":"buy","size":"1","price":"100"}]"#,
        )],
        "POST /api/v1/hf/orders/multi",
    ),
    private(
        "place_spot_batch_market_orders",
        Host::Spot,
        &[(
            "orders",
            r#"[{"product_symbol":"BTC-USDT-SPOT","side":"buy","size":"1"}]"#,
        )],
        "POST /api/v1/hf/orders/multi",
    ),
    private(
        "alter_spot_order",
        Host::Spot,
        &[
            ("product_symbol", SPOT),
            ("orderId", "1"),
            ("newPrice", "101"),
        ],
        "POST /api/v1/hf/orders/alter",
    ),
    private(
        "cancel_spot_order",
        Host::Spot,
        &[("orderId", "abc"), ("product_symbol", SPOT)],
        "DELETE /api/v1/hf/orders/abc?symbol=BTC-USDT",
    ),
    private(
        "cancel_spot_all_orders_by_symbol",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "DELETE /api/v1/hf/orders?symbol=BTC-USDT",
    ),
    private(
        "cancel_spot_all_orders",
        Host::Spot,
        &[],
        "DELETE /api/v1/hf/orders/cancelAll",
    ),
    private(
        "get_spot_open_orders",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/hf/orders/active/page",
    ),
    private(
        "get_spot_trade_history",
        Host::Spot,
        &[("product_symbol", SPOT)],
        "GET /api/v1/hf/fills",
    ),
    // Futures orders.
    private(
        "place_futures_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("side", "buy"),
            ("type", "limit"),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "test_futures_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("side", "buy"),
            ("type", "limit"),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders/test",
    ),
    private(
        "place_futures_market_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("side", "buy"),
            ("size", "1"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_market_buy_order",
        Host::Futures,
        &[("product_symbol", SWAP), ("size", "1"), ("leverage", "3")],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_market_sell_order",
        Host::Futures,
        &[("product_symbol", SWAP), ("size", "1"), ("leverage", "3")],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_limit_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("side", "sell"),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_limit_buy_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_limit_sell_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_post_only_limit_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("side", "buy"),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_post_only_limit_buy_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "place_futures_post_only_limit_sell_order",
        Host::Futures,
        &[
            ("product_symbol", SWAP),
            ("size", "1"),
            ("price", "100"),
            ("leverage", "3"),
        ],
        "POST /api/v1/orders",
    ),
    private(
        "get_futures_order_list",
        Host::Futures,
        &[("status", "active")],
        "GET /api/v1/orders?",
    ),
    private(
        "get_futures_order",
        Host::Futures,
        &[("orderId", "abc")],
        "GET /api/v1/orders/abc",
    ),
    private(
        "get_futures_order_by_client_oid",
        Host::Futures,
        &[("clientOid", "cid")],
        "GET /api/v1/orders/byClientOid?clientOid=cid",
    ),
    private(
        "cancel_futures_order",
        Host::Futures,
        &[("orderId", "abc")],
        "DELETE /api/v1/orders/abc",
    ),
    private(
        "cancel_futures_order_by_client_oid",
        Host::Futures,
        &[("clientOid", "cid"), ("product_symbol", SWAP)],
        "DELETE /api/v1/orders/client-order/cid?symbol=XBTUSDTM",
    ),
    private(
        "cancel_futures_all_orders",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "DELETE /api/v3/orders?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_open_order_value",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/openOrderStatistics?symbol=XBTUSDTM",
    ),
    private(
        "get_futures_trade_history",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/fills",
    ),
    private(
        "get_futures_recent_trade_history",
        Host::Futures,
        &[("product_symbol", SWAP)],
        "GET /api/v1/recentFills",
    ),
];

fn one_shot_server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 8192];
        let size = stream.read(&mut buffer).expect("read");
        let mut request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        while !request.contains("\r\n\r\n") {
            let size = stream.read(&mut buffer).expect("read headers");
            assert!(size > 0, "request ended before headers were complete");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        let content_length = request
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("content-length: ")
                    .and_then(|value| value.trim().parse::<usize>().ok())
            })
            .unwrap_or(0);
        while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < content_length {
            let size = stream.read(&mut buffer).expect("read body");
            assert!(size > 0, "request ended before the declared body length");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        let body = br#"{"code":"200000","data":{}}"#;
        let head = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
            body.len()
        );
        stream.write_all(head.as_bytes()).expect("write head");
        stream.write_all(body).expect("write body");
        request
    });
    (format!("http://{address}"), handle)
}

async fn run_case(case: &Case) -> String {
    let (base_url, handle) = one_shot_server();
    let (spot, futures) = match case.host {
        Host::Spot => (base_url, CLOSED_PORT.to_string()),
        Host::Futures => (CLOSED_PORT.to_string(), base_url),
    };
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        spot,
        futures,
    )
    .expect("client");
    let params = case
        .params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect::<Vec<_>>();
    let result = if case.private {
        client.private_request(case.name, params).await
    } else {
        client.public_request(case.name, params).await
    };
    if let Err(error) = result {
        panic!("{} failed: {error}", case.name);
    }
    handle.join().expect("server")
}

fn assert_route(case: &Case, request: &str) {
    let request_line = request.lines().next().unwrap_or_default();
    let target = request_line
        .strip_suffix(" HTTP/1.1")
        .unwrap_or(request_line);
    let route_path = case.route.split('?').next().unwrap_or(case.route);
    let target_path = target.split('?').next().unwrap_or(target);
    assert_eq!(
        target_path, route_path,
        "{} sent `{request_line}`, expected `{}`",
        case.name, case.route
    );
    if let Some((_, expected_query)) = case.route.split_once('?') {
        let query = target.split_once('?').map_or("", |(_, query)| query);
        for pair in expected_query.split('&').filter(|pair| !pair.is_empty()) {
            assert!(
                query.split('&').any(|actual| actual == pair),
                "{} query `{query}` is missing `{pair}`",
                case.name
            );
        }
    }
    if case.private {
        let lower = request.to_ascii_lowercase();
        assert!(
            lower.contains("kc-api-sign:") && lower.contains("kc-api-key: key"),
            "{} was not signed",
            case.name
        );
    }
}

#[tokio::test]
async fn every_public_dispatch_name_hits_documented_route() {
    for case in PUBLIC_CASES {
        let request = run_case(case).await;
        assert_route(case, &request);
        assert!(
            !request.to_ascii_lowercase().contains("kc-api-sign:"),
            "{} public request must not be signed",
            case.name
        );
    }
}

#[tokio::test]
async fn every_private_dispatch_name_hits_documented_route() {
    for case in PRIVATE_CASES {
        let request = run_case(case).await;
        assert_route(case, &request);
        if case.route.starts_with("POST ") {
            let body = request.split("\r\n\r\n").nth(1).unwrap_or_default();
            let value: serde_json::Value = serde_json::from_str(body)
                .unwrap_or_else(|error| panic!("{} body is not JSON ({error}): {body}", case.name));
            assert!(
                value.is_object() || value.is_array(),
                "{} body must be a JSON document",
                case.name
            );
        }
    }
}

#[tokio::test]
async fn futures_orders_resolve_contract_symbol_in_body() {
    let case = &PRIVATE_CASES
        .iter()
        .find(|case| case.name == "place_futures_limit_buy_order")
        .expect("case");
    let request = run_case(case).await;
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(body["symbol"], "XBTUSDTM");
    assert_eq!(body["side"], "buy");
    assert_eq!(body["type"], "limit");
    assert_eq!(body["price"], "100");
    assert!(
        body["clientOid"]
            .as_str()
            .is_some_and(|oid| !oid.is_empty())
    );
}

#[tokio::test]
async fn spot_post_only_helpers_force_post_only_flag() {
    for name in [
        "place_spot_post_only_limit_buy_order",
        "place_spot_post_only_limit_sell_order",
    ] {
        let case = PRIVATE_CASES
            .iter()
            .find(|case| case.name == name)
            .expect("case");
        let request = run_case(case).await;
        let body: serde_json::Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
        assert_eq!(body["symbol"], "BTC-USDT", "{name}");
        assert_eq!(body["postOnly"], true, "{name}");
        assert_eq!(body["type"], "limit", "{name}");
        let expected_side = if name.contains("buy") { "buy" } else { "sell" };
        assert_eq!(body["side"], expected_side, "{name}");
    }
}

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_before_network() {
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        CLOSED_PORT.into(),
        CLOSED_PORT.into(),
    )
    .expect("client");
    let public_error = client
        .public_request("get_not_a_real_endpoint", Vec::new())
        .await
        .expect_err("unknown public name");
    assert!(public_error.to_string().contains("unsupported"));
    let private_error = client
        .private_request("get_not_a_real_endpoint", Vec::new())
        .await
        .expect_err("unknown private name");
    assert!(private_error.to_string().contains("unsupported"));
}

/// Side/type-fixed helpers such as `place_spot_limit_buy_order` must not
/// require the caller to repeat the fixed side or type.
#[tokio::test]
async fn side_and_type_fixed_helpers_do_not_require_side_or_type() {
    for (case, side, order_type) in [
        (
            private(
                "place_spot_limit_buy_order",
                Host::Spot,
                &[("product_symbol", SPOT), ("size", "1"), ("price", "100")],
                "POST /api/v1/hf/orders",
            ),
            "buy",
            "limit",
        ),
        (
            private(
                "place_spot_market_order",
                Host::Spot,
                &[("product_symbol", SPOT), ("side", "buy"), ("size", "1")],
                "POST /api/v1/hf/orders",
            ),
            "buy",
            "market",
        ),
        (
            private(
                "place_futures_market_sell_order",
                Host::Futures,
                &[("product_symbol", SWAP), ("size", "1"), ("leverage", "3")],
                "POST /api/v1/orders",
            ),
            "sell",
            "market",
        ),
    ] {
        let request = run_case(&case).await;
        assert_route(&case, &request);
        let body = request_body(&request);
        assert_eq!(body["side"], side, "{}", case.name);
        assert_eq!(body["type"], order_type, "{}", case.name);
    }
}

fn request_body(request: &str) -> serde_json::Value {
    serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON")
}

fn offline_private_client() -> KucoinClient {
    KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        CLOSED_PORT.into(),
        CLOSED_PORT.into(),
    )
    .expect("client")
}

/// Names declared in `wrappers.rs`, split into its `public [...]` and
/// `private [...]` blocks, so a new wrapper without a route case fails here.
fn declared_wrapper_names() -> (Vec<&'static str>, Vec<&'static str>) {
    let source = include_str!("../wrappers.rs");
    let mut public = Vec::new();
    let mut private = Vec::new();
    let mut section: Option<bool> = None;
    for line in source.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("public [") {
            section = Some(false);
        } else if trimmed.starts_with("private [") {
            section = Some(true);
        } else if trimmed.starts_with("];") {
            section = None;
        } else if let (Some(is_private), Some((name, _))) = (section, trimmed.split_once('('))
            && !name.is_empty()
            && name.chars().all(|c| c.is_ascii_lowercase() || c == '_')
        {
            if is_private {
                private.push(name);
            } else {
                public.push(name);
            }
        }
    }
    (public, private)
}

#[test]
fn every_declared_wrapper_has_a_route_case() {
    let (public, private) = declared_wrapper_names();
    assert!(
        public.len() > 10 && private.len() > 50,
        "wrapper parse failed"
    );
    let missing_public: Vec<_> = public
        .iter()
        .filter(|name| !PUBLIC_CASES.iter().any(|case| case.name == **name))
        .collect();
    let missing_private: Vec<_> = private
        .iter()
        .filter(|name| !PRIVATE_CASES.iter().any(|case| case.name == **name))
        .collect();
    assert!(
        missing_public.is_empty(),
        "public wrappers without a route case: {missing_public:?}"
    );
    assert!(
        missing_private.is_empty(),
        "private wrappers without a route case: {missing_private:?}"
    );
}

#[tokio::test]
async fn uta_amend_resolves_futures_contract_symbol() {
    // The official UTA V2 amend endpoint currently supports futures only.
    let case = private(
        "amend_uta_order",
        Host::Spot,
        &[
            ("product_symbol", SWAP),
            ("orderId", "1"),
            ("newPrice", "101"),
        ],
        "POST /api/ua/v2/unified/order/amend",
    );
    let request = run_case(&case).await;
    assert_route(&case, &request);
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(body["symbol"], "XBTUSDTM");
    assert_eq!(body["orderId"], "1");
    assert_eq!(body["newPrice"], "101");
}

/// `set_dcp` uses the current spot dead-man switch
/// (`POST /api/v1/hf/orders/dead-cancel-all`), whose documented `symbols`
/// field is a comma-separated string; omitted or empty means all pairs.
#[tokio::test]
async fn dcp_sends_documented_symbols_field() {
    for (params, expected) in [
        (
            &[("timeout", "10"), ("symbols", r#"["BTC-USDT","ETH-USDT"]"#)][..],
            Some("BTC-USDT,ETH-USDT"),
        ),
        (
            &[("timeout", "10"), ("symbols", "BTC-USDT, ETH-USDT")][..],
            Some("BTC-USDT,ETH-USDT"),
        ),
        (&[("timeout", "10"), ("symbols", "[]")][..], Some("")),
        (&[("timeout", "10")][..], None),
    ] {
        let case = private(
            "set_dcp",
            Host::Spot,
            params,
            "POST /api/v1/hf/orders/dead-cancel-all",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        let body = request_body(&request);
        assert_eq!(body["timeout"], 10);
        assert_eq!(
            body.get("symbols").and_then(|value| value.as_str()),
            expected
        );
    }
}

#[tokio::test]
async fn dcp_validates_timeout_and_symbol_count_before_network() {
    let client = offline_private_client();
    for timeout in ["4", "86401", "0", "abc"] {
        let error = client
            .private_request("set_dcp", vec![("timeout".into(), timeout.into())])
            .await
            .expect_err("invalid timeout");
        assert!(error.to_string().contains("timeout"), "{timeout}: {error}");
    }
    let too_many = (0..51)
        .map(|index| format!("C{index}-USDT"))
        .collect::<Vec<_>>()
        .join(",");
    let error = client
        .private_request(
            "set_dcp",
            vec![
                ("timeout".into(), "-1".into()),
                ("symbols".into(), too_many),
            ],
        )
        .await
        .expect_err("too many symbols");
    assert!(error.to_string().contains("50"));
    let error = client
        .private_request(
            "set_dcp",
            vec![
                ("timeout".into(), "10".into()),
                ("tradeType".into(), "SPOT".into()),
            ],
        )
        .await
        .expect_err("tradeType is not a field of the spot DCP");
    assert!(error.to_string().contains("tradeType"));
}

#[tokio::test]
async fn spot_orderbook_selects_documented_depth() {
    let case = public(
        "get_spot_orderbook",
        Host::Spot,
        &[("product_symbol", SPOT), ("depth", "100")],
        "GET /api/v1/market/orderbook/level2_100?symbol=BTC-USDT",
    );
    let request = run_case(&case).await;
    assert_route(&case, &request);
    let client = KucoinClient::public(Duration::from_secs(10)).expect("client");
    let error = client
        .public_request(
            "get_spot_orderbook",
            vec![
                ("product_symbol".into(), SPOT.into()),
                ("depth".into(), "50".into()),
            ],
        )
        .await
        .expect_err("unsupported depth");
    assert!(error.to_string().contains("depth"));
}

#[tokio::test]
async fn uta_place_requires_size_unit_and_forwards_stp_and_cancel_after() {
    let case = private(
        "place_uta_order",
        Host::Spot,
        &[
            ("tradeType", "SPOT"),
            ("product_symbol", SPOT),
            ("side", "BUY"),
            ("orderType", "LIMIT"),
            ("size", "1"),
            ("sizeUnit", "BASECCY"),
            ("price", "100"),
            ("timeInForce", "GTT"),
            ("cancelAfter", "60"),
            ("stp", "CN"),
        ],
        "POST /api/ua/v2/unified/order/place",
    );
    let request = run_case(&case).await;
    assert_route(&case, &request);
    let body = request_body(&request);
    assert_eq!(body["sizeUnit"], "BASECCY");
    assert_eq!(body["stp"], "CN");
    assert_eq!(body["cancelAfter"], 60);

    let client = offline_private_client();
    let error = client
        .private_request(
            "place_uta_order",
            vec![
                ("tradeType".into(), "SPOT".into()),
                ("product_symbol".into(), SPOT.into()),
                ("side".into(), "BUY".into()),
                ("orderType".into(), "MARKET".into()),
                ("size".into(), "1".into()),
            ],
        )
        .await
        .expect_err("sizeUnit is required");
    assert!(error.to_string().contains("sizeUnit"));
}

#[tokio::test]
async fn uta_amend_forwards_documented_fields_and_rejects_spot_symbols() {
    let case = private(
        "amend_uta_order",
        Host::Spot,
        &[
            ("product_symbol", SWAP),
            ("clientOid", "abc"),
            ("newSize", "2"),
            ("sizeUnit", "UNIT"),
            ("cxlOnFail", "true"),
            ("tpTriggerPrice", "120"),
            ("tpTriggerPriceType", "MP"),
            ("slTriggerPrice", "80"),
            ("slTriggerPriceType", "TP"),
        ],
        "POST /api/ua/v2/unified/order/amend",
    );
    let request = run_case(&case).await;
    assert_route(&case, &request);
    let body = request_body(&request);
    assert_eq!(body["symbol"], "XBTUSDTM");
    assert_eq!(body["sizeUnit"], "UNIT");
    assert_eq!(body["cxlOnFail"], true);
    assert_eq!(body["tpTriggerPrice"], "120");
    assert_eq!(body["slTriggerPriceType"], "TP");

    let client = offline_private_client();
    for symbol in [SPOT, "BTC-USDT"] {
        let error = client
            .private_request(
                "amend_uta_order",
                vec![
                    ("product_symbol".into(), symbol.into()),
                    ("orderId".into(), "1".into()),
                    ("newPrice".into(), "101".into()),
                ],
            )
            .await
            .expect_err("spot amend is not supported");
        assert!(
            error.to_string().contains("futures only"),
            "{symbol}: {error}"
        );
    }
}

#[tokio::test]
async fn uta_trade_type_and_batch_symbols_reject_mismatches() {
    let client = offline_private_client();
    for (trade_type, symbol) in [("MARGIN", SWAP), ("SPOT", "XBTUSDTM"), ("FUTURES", SPOT)] {
        for method in ["get_uta_leverage", "batch_cancel_uta_orders"] {
            let mut params = vec![("tradeType".into(), trade_type.into())];
            if method == "batch_cancel_uta_orders" {
                params.push((
                    "cancelOrderList".into(),
                    serde_json::json!([{"symbol":symbol,"orderId":"123"}]).to_string(),
                ));
            } else {
                params.push(("product_symbol".into(), symbol.into()));
            }
            let error = client.private_request(method, params).await.unwrap_err();
            assert!(error.to_string().contains("tradeType"), "{method}: {error}");
        }
    }
}

#[tokio::test]
async fn uta_risk_and_batch_endpoints_follow_official_payloads() {
    {
        let case = private(
            "batch_cancel_uta_orders",
            Host::Spot,
            &[
                ("tradeType", "FUTURES"),
                (
                    "cancelOrderList",
                    "[{\"symbol\": \"BTC-USDT-SWAP\", \"orderId\": \"1\", \"clientOid\": \"c\"}, {\"symbol\": \"ETHUSDTM\", \"clientOid\": \"d\"}]",
                ),
            ],
            "POST /api/ua/v2/unified/order/cancel-batch",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"tradeType": "FUTURES", "cancelOrderList": [{"symbol": "XBTUSDTM", "orderId": "1", "clientOid": "c"}, {"symbol": "ETHUSDTM", "clientOid": "d"}]})
        );
    }
    {
        let case = private(
            "cancel_uta_orders_by_symbol",
            Host::Spot,
            &[
                ("tradeType", "FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
                ("orderFilter", "ADVANCED"),
                ("marginMode", "ISOLATED"),
            ],
            "POST /api/ua/v2/unified/order/cancel-all",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"tradeType": "FUTURES", "symbol": "XBTUSDTM", "orderFilter": "ADVANCED", "marginMode": "ISOLATED"})
        );
    }
    {
        let case = private(
            "get_uta_margin_mode",
            Host::Spot,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET /api/ua/v2/unified/position/margin-mode",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert!(request.lines().next().unwrap().contains("symbol=XBTUSDTM"));
    }
    {
        let case = private(
            "set_uta_margin_mode",
            Host::Spot,
            &[("product_symbol", "BTC-USDT-SWAP"), ("marginMode", "CROSS")],
            "POST /api/ua/v2/unified/position/margin-mode",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"symbol": "XBTUSDTM", "marginMode": "CROSS"})
        );
    }
    {
        let case = private(
            "modify_uta_position_margin",
            Host::Spot,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("type", "WITHDRAW"),
                ("amount", "1.25"),
            ],
            "POST /api/ua/v2/unified/position/modify-margin",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"symbol": "XBTUSDTM", "type": "WITHDRAW", "amount": 1.25, "tradeType": "FUTURES"})
        );
    }
    {
        let case = private(
            "get_uta_max_order_quantity",
            Host::Spot,
            &[
                ("tradeType", "SPOT"),
                ("product_symbol", "BTC-USDT-SPOT"),
                ("price", "123.45"),
            ],
            "GET /api/ua/v2/order/max-order-quantity",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert!(request.lines().next().unwrap().contains("symbol=BTC-USDT"));
        assert!(request.lines().next().unwrap().contains("tradeType=SPOT"));
        assert!(request.lines().next().unwrap().contains("price=123.45"));
    }
    {
        let case = private(
            "get_uta_leverage",
            Host::Spot,
            &[
                ("tradeType", "MARGIN"),
                ("currency", "USDT"),
                ("marginMode", "CROSS"),
            ],
            "GET /api/ua/v2/unified/account/leverage",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert!(request.lines().next().unwrap().contains("tradeType=MARGIN"));
        assert!(request.lines().next().unwrap().contains("currency=USDT"));
        assert!(request.lines().next().unwrap().contains("marginMode=CROSS"));
    }
    {
        let case = private(
            "modify_uta_futures_leverage",
            Host::Spot,
            &[("product_symbol", "BTC-USDT-SWAP"), ("leverage", "3")],
            "POST /api/ua/v2/unified/account/modify-leverage",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"symbol": "XBTUSDTM", "leverage": "3"})
        );
    }
    {
        let case = private(
            "modify_uta_cross_margin_leverage",
            Host::Spot,
            &[("leverage", "2"), ("currency", "USDT")],
            "POST /api/ua/v2/unified/account/modify-leverage-margin-cross",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert_eq!(
            request_body(&request),
            serde_json::json!({"currency": "USDT", "leverage": "2"})
        );
    }
    {
        let case = private(
            "get_uta_position_history",
            Host::Spot,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("lastId", "1234"),
                ("pageSize", "20"),
            ],
            "GET /api/ua/v2/position/history",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert!(request.lines().next().unwrap().contains("symbol=XBTUSDTM"));
        assert!(request.lines().next().unwrap().contains("lastId=1234"));
        assert!(request.lines().next().unwrap().contains("pageSize=20"));
    }
    {
        let case = private(
            "get_uta_funding_history",
            Host::Spot,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startAt", "1700000000000"),
                ("endAt", "1700000060000"),
                ("lastId", "42"),
                ("pageSize", "200"),
            ],
            "GET /api/ua/v2/position/funding-history",
        );
        let request = run_case(&case).await;
        assert_route(&case, &request);
        assert!(request.lines().next().unwrap().contains("symbol=XBTUSDTM"));
        assert!(
            request
                .lines()
                .next()
                .unwrap()
                .contains("startAt=1700000000000")
        );
        assert!(
            request
                .lines()
                .next()
                .unwrap()
                .contains("endAt=1700000060000")
        );
        assert!(request.lines().next().unwrap().contains("lastId=42"));
        assert!(request.lines().next().unwrap().contains("pageSize=200"));
    }
}

#[tokio::test]
async fn uta_batch_and_risk_reject_invalid_inputs_before_transport() {
    let client = offline_private_client();
    for orders in [
        serde_json::json!([]),
        serde_json::json!([null]),
        serde_json::json!([{"symbol":"XBTUSDTM"}]),
        serde_json::json!([{"symbol":"XBTUSDTM","orderId":42}]),
        serde_json::json!([{"orderId":"42"}]),
        serde_json::json!([{"symbol":"XBTUSDTM","orderId":"42","typo":true}]),
        serde_json::Value::Array(vec![
            serde_json::json!({"symbol":"XBTUSDTM","orderId":"42"});
            21
        ]),
    ] {
        let error = client
            .private_request(
                "batch_cancel_uta_orders",
                vec![
                    ("tradeType".into(), "FUTURES".into()),
                    ("cancelOrderList".into(), orders.to_string()),
                ],
            )
            .await
            .expect_err("invalid batch");
        assert!(
            matches!(error, crate::DcexError::InvalidInput(_)),
            "{error}"
        );
    }
    for (name, params) in [
        (
            "set_uta_margin_mode",
            vec![("product_symbol", SWAP), ("marginMode", "INVALID")],
        ),
        (
            "modify_uta_futures_leverage",
            vec![("product_symbol", SWAP), ("leverage", "0")],
        ),
        (
            "modify_uta_position_margin",
            vec![
                ("product_symbol", SWAP),
                ("type", "DEPOSIT"),
                ("amount", "-1"),
            ],
        ),
        ("get_uta_leverage", vec![("tradeType", "SPOT")]),
        ("get_uta_position_history", vec![("pageSize", "abc")]),
    ] {
        let error = client
            .private_request(
                name,
                params
                    .into_iter()
                    .map(|(k, v)| (k.into(), v.into()))
                    .collect(),
            )
            .await
            .expect_err("invalid risk parameter");
        assert!(
            matches!(error, crate::DcexError::InvalidInput(_)),
            "{name}: {error}"
        );
    }
}

#[tokio::test]
async fn every_typed_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        url.clone(),
        url.clone(),
    )
    .expect("client");
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "kucoin",
        "KucoinClient",
        |name, public, params| {
            let client = &client;
            async move {
                if public {
                    client.public_request(name, params).await
                } else {
                    client.private_request(name, params).await
                }
            }
        },
    )
    .await;
}
