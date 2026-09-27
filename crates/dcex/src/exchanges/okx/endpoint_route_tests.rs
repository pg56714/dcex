//! Offline route coverage: every OKX dispatch name must reach its documented
//! REST path with the documented HTTP method and signing mode.

use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;
use std::time::Duration;

use serde_json::Value;

use super::OkxClient;

struct Case {
    name: &'static str,
    public: bool,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    path: &'static str,
    expect: &'static [&'static str],
}

const fn public(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    path: &'static str,
    expect: &'static [&'static str],
) -> Case {
    Case {
        name,
        public: true,
        params,
        method: "GET",
        path,
        expect,
    }
}

const fn get(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    path: &'static str,
    expect: &'static [&'static str],
) -> Case {
    Case {
        name,
        public: false,
        params,
        method: "GET",
        path,
        expect,
    }
}

const fn post(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    path: &'static str,
    expect: &'static [&'static str],
) -> Case {
    Case {
        name,
        public: false,
        params,
        method: "POST",
        path,
        expect,
    }
}

const SWAP: (&str, &str) = ("product_symbol", "BTC-USDT-SWAP");
const SPRD: (&str, &str) = ("sprdId", "BTC-USDT_BTC-USDT-SWAP");
const LIMIT_ORDER: &[(&str, &str)] = &[
    SWAP,
    ("tdMode", "cross"),
    ("side", "buy"),
    ("sz", "1"),
    ("px", "1"),
];
const SIDED_ORDER: &[(&str, &str)] = &[SWAP, ("tdMode", "cross"), ("sz", "1"), ("px", "1")];

const CASES: &[Case] = &[
    Case {
        name: "get_bill_types",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/account/subtypes",
        expect: &[],
    },
    Case {
        name: "simulate_positions",
        public: false,
        params: &[],
        method: "POST",
        path: "/api/v5/account/position-builder",
        expect: &[],
    },
    Case {
        name: "get_position_margin_graph",
        public: false,
        params: &[("type", "mmr"), ("mmrConfig", "{\"acctLv\":\"4\"}")],
        method: "POST",
        path: "/api/v5/account/position-builder-graph",
        expect: &[],
    },
    Case {
        name: "move_positions",
        public: false,
        params: &[
            ("fromAcct", "0"),
            ("toAcct", "subacct1"),
            (
                "legs",
                "[{\"from\":{\"posId\":\"1\",\"sz\":\"1\",\"side\":\"buy\"},\"to\":{}}]",
            ),
            ("clientId", "move1"),
        ],
        method: "POST",
        path: "/api/v5/account/move-positions",
        expect: &[],
    },
    Case {
        name: "get_move_positions_history",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/account/move-positions-history",
        expect: &[],
    },
    Case {
        name: "adjust_demo_balance",
        public: false,
        params: &[
            ("type", "increase"),
            ("adjustments", "[{\"ccy\":\"BTC\",\"amt\":\"0.1\"}]"),
        ],
        method: "POST",
        path: "/api/v5/account/demo-adjust-balance",
        expect: &[],
    },
    Case {
        name: "get_books_rpi",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/books-rpi",
        expect: &[],
    },
    Case {
        name: "get_platform_24_volume",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/market/platform-24-volume",
        expect: &[],
    },
    Case {
        name: "get_call_auction_details",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/call-auction-details",
        expect: &[],
    },
    Case {
        name: "rfq_create_rfq",
        public: false,
        params: &[
            ("counterparties", "[\"maker1\"]"),
            (
                "legs",
                "[{\"instId\":\"BTC-USDT-SWAP\",\"sz\":\"1\",\"side\":\"buy\"}]",
            ),
        ],
        method: "POST",
        path: "/api/v5/rfq/create-rfq",
        expect: &[],
    },
    Case {
        name: "get_rfq_counterparties",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/rfq/counterparties",
        expect: &[],
    },
    Case {
        name: "rfq_cancel_rfq",
        public: false,
        params: &[("rfqId", "1")],
        method: "POST",
        path: "/api/v5/rfq/cancel-rfq",
        expect: &[],
    },
    Case {
        name: "rfq_cancel_batch_rfqs",
        public: false,
        params: &[("rfqIds", "[\"1\"]")],
        method: "POST",
        path: "/api/v5/rfq/cancel-batch-rfqs",
        expect: &[],
    },
    Case {
        name: "rfq_cancel_all_rfqs",
        public: false,
        params: &[],
        method: "POST",
        path: "/api/v5/rfq/cancel-all-rfqs",
        expect: &[],
    },
    Case {
        name: "rfq_execute_quote",
        public: false,
        params: &[("rfqId", "1"), ("quoteId", "1")],
        method: "POST",
        path: "/api/v5/rfq/execute-quote",
        expect: &[],
    },
    Case {
        name: "get_rfq_rfqs",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/rfq/rfqs",
        expect: &[],
    },
    Case {
        name: "get_rfq_quotes",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/rfq/quotes",
        expect: &[],
    },
    Case {
        name: "get_rfq_trades",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/rfq/trades",
        expect: &[],
    },
    Case {
        name: "get_block_tickers",
        public: true,
        params: &[("instType", "SWAP")],
        method: "GET",
        path: "/api/v5/market/block-tickers",
        expect: &[],
    },
    Case {
        name: "get_block_ticker",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/block-ticker",
        expect: &[],
    },
    Case {
        name: "get_rfq_public_trades",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/rfq/public-trades",
        expect: &[],
    },
    Case {
        name: "get_block_trades",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/public/block-trades",
        expect: &[],
    },
    Case {
        name: "get_estimated_settlement_info",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/public/estimated-settlement-info",
        expect: &[],
    },
    Case {
        name: "get_settlement_history",
        public: true,
        params: &[("instFamily", "BTC-USDT")],
        method: "GET",
        path: "/api/v5/public/settlement-history",
        expect: &[],
    },
    Case {
        name: "get_insurance_fund",
        public: true,
        params: &[("instType", "SWAP"), ("instFamily", "BTC-USDT")],
        method: "GET",
        path: "/api/v5/public/insurance-fund",
        expect: &[],
    },
    Case {
        name: "get_premium_history",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/public/premium-history",
        expect: &[],
    },
    Case {
        name: "get_index_candles",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/index-candles",
        expect: &[],
    },
    Case {
        name: "get_history_index_candles",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/history-index-candles",
        expect: &[],
    },
    Case {
        name: "get_history_mark_price_candles",
        public: true,
        params: &[("instId", "BTC-USDT-SWAP")],
        method: "GET",
        path: "/api/v5/market/history-mark-price-candles",
        expect: &[],
    },
    Case {
        name: "get_exchange_rate",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/market/exchange-rate",
        expect: &[],
    },
    Case {
        name: "get_index_components",
        public: true,
        params: &[("index", "BTC-USDT")],
        method: "GET",
        path: "/api/v5/market/index-components",
        expect: &[],
    },
    Case {
        name: "get_economic_calendar",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/public/economic-calendar",
        expect: &[],
    },
    Case {
        name: "get_market_data_history",
        public: true,
        params: &[
            ("module", "1"),
            ("instType", "SWAP"),
            ("dateAggrType", "daily"),
            ("begin", "1700000000000"),
            ("end", "1700000001000"),
            ("instFamilyList", "BTC-USDT"),
        ],
        method: "GET",
        path: "/api/v5/public/market-data-history",
        expect: &[],
    },
    Case {
        name: "get_delta_hedge_currencies",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/public/delta-hedge-currencies",
        expect: &[],
    },
    Case {
        name: "get_loan_ratio",
        public: true,
        params: &[("ccy", "BTC")],
        method: "GET",
        path: "/api/v5/rubik/stat/margin/loan-ratio",
        expect: &[],
    },
    Case {
        name: "get_non_tradable_assets",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/asset/non-tradable-assets",
        expect: &[],
    },
    Case {
        name: "create_sub_account",
        public: false,
        params: &[("subAcct", "subacct1"), ("type", "1")],
        method: "POST",
        path: "/api/v5/users/subaccount/create-subaccount",
        expect: &[],
    },
    Case {
        name: "create_sub_account_api_key",
        public: false,
        params: &[
            ("subAcct", "subacct1"),
            ("label", "trading"),
            ("passphrase", "Trader123!"),
        ],
        method: "POST",
        path: "/api/v5/users/subaccount/apikey",
        expect: &[],
    },
    Case {
        name: "get_sub_account_api_keys",
        public: false,
        params: &[("subAcct", "subacct1")],
        method: "GET",
        path: "/api/v5/users/subaccount/apikey",
        expect: &[],
    },
    Case {
        name: "modify_sub_account_api_key",
        public: false,
        params: &[("subAcct", "subacct1"), ("apiKey", "api-key")],
        method: "POST",
        path: "/api/v5/users/subaccount/modify-apikey",
        expect: &[],
    },
    Case {
        name: "delete_sub_account_api_key",
        public: false,
        params: &[("subAcct", "subacct1"), ("apiKey", "api-key")],
        method: "POST",
        path: "/api/v5/users/subaccount/delete-apikey",
        expect: &[],
    },
    Case {
        name: "set_sub_account_transfer_out",
        public: false,
        params: &[("subAcct", "subacct1")],
        method: "POST",
        path: "/api/v5/users/subaccount/set-transfer-out",
        expect: &[],
    },
    Case {
        name: "get_announcements",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/support/announcements",
        expect: &[],
    },
    Case {
        name: "get_announcement_types",
        public: true,
        params: &[],
        method: "GET",
        path: "/api/v5/support/announcement-types",
        expect: &[],
    },
    Case {
        name: "set_fee_type",
        public: false,
        params: &[("feeType", "1")],
        method: "POST",
        path: "/api/v5/account/set-fee-type",
        expect: &[],
    },
    Case {
        name: "set_risk_offset_amount",
        public: false,
        params: &[("ccy", "BTC"), ("clSpotInUseAmt", "0")],
        method: "POST",
        path: "/api/v5/account/set-riskOffset-amt",
        expect: &[],
    },
    Case {
        name: "activate_options",
        public: false,
        params: &[],
        method: "POST",
        path: "/api/v5/account/activate-option",
        expect: &[],
    },
    Case {
        name: "set_auto_loan",
        public: false,
        params: &[("autoLoan", "false")],
        method: "POST",
        path: "/api/v5/account/set-auto-loan",
        expect: &[],
    },
    Case {
        name: "preset_account_level_switch",
        public: false,
        params: &[("acctLv", "2"), ("lever", "5")],
        method: "POST",
        path: "/api/v5/account/account-level-switch-preset",
        expect: &[],
    },
    Case {
        name: "precheck_account_level_switch",
        public: false,
        params: &[("acctLv", "3")],
        method: "GET",
        path: "/api/v5/account/set-account-switch-precheck",
        expect: &[],
    },
    Case {
        name: "set_collateral_assets",
        public: false,
        params: &[
            ("type", "custom"),
            ("collateralEnabled", "true"),
            ("ccyList", "[\"BTC\",\"ETH\"]"),
        ],
        method: "POST",
        path: "/api/v5/account/set-collateral-assets",
        expect: &[],
    },
    Case {
        name: "set_settlement_currency",
        public: false,
        params: &[("settleCcy", "USDC")],
        method: "POST",
        path: "/api/v5/account/set-settle-currency",
        expect: &[],
    },
    Case {
        name: "set_trading_config",
        public: false,
        params: &[("type", "stgyType"), ("stgyType", "1")],
        method: "POST",
        path: "/api/v5/account/set-trading-config",
        expect: &[],
    },
    Case {
        name: "precheck_delta_neutral",
        public: false,
        params: &[("stgyType", "1")],
        method: "GET",
        path: "/api/v5/account/precheck-set-delta-neutral",
        expect: &[],
    },
    Case {
        name: "get_repayment_currencies",
        public: false,
        params: &[],
        method: "GET",
        path: "/api/v5/trade/one-click-repay-currency-list-v2",
        expect: &[],
    },
    Case {
        name: "repay_debt",
        public: false,
        params: &[("debtCcy", "USDT"), ("repayCcyList", "[\"USDC\",\"BTC\"]")],
        method: "POST",
        path: "/api/v5/trade/one-click-repay-v2",
        expect: &[],
    },
    Case {
        name: "get_repayment_history",
        public: false,
        params: &[("limit", "100")],
        method: "GET",
        path: "/api/v5/trade/one-click-repay-history-v2",
        expect: &[],
    },
    Case {
        name: "get_spread_order_history_archive",
        public: false,
        params: &[("instType", "SWAP"), ("limit", "100")],
        method: "GET",
        path: "/api/v5/sprd/orders-history-archive",
        expect: &[],
    },
    public("get_server_time", &[], "/api/v5/public/time", &[]),
    post(
        "set_isolated_mode",
        &[("isoMode", "automatic"), ("type", "MARGIN")],
        "/api/v5/account/set-isolated-mode",
        &[],
    ),
    get(
        "get_account_risk_state",
        &[],
        "/api/v5/account/risk-state",
        &[],
    ),
    get("get_greeks", &[], "/api/v5/account/greeks", &[]),
    get(
        "get_pm_position_tiers",
        &[("instType", "SWAP"), ("instFamily", "BTC-USDT")],
        "/api/v5/account/position-tiers",
        &[],
    ),
    post(
        "set_account_level",
        &[("acctLv", "3")],
        "/api/v5/account/set-account-level",
        &[],
    ),
    get(
        "get_collateral_assets",
        &[("ccy", "BTC,ETH"), ("collateralEnabled", "false")],
        "/api/v5/account/collateral-assets",
        &[],
    ),
    public(
        "get_ticker",
        &[("instId", "BTC-USDT-SWAP")],
        "/api/v5/market/ticker",
        &[],
    ),
    public(
        "get_full_orderbook",
        &[("instId", "BTC-USDT-SWAP"), ("sz", "5000")],
        "/api/v5/market/books-full",
        &[],
    ),
    public(
        "get_candles_history",
        &[("instId", "BTC-USDT-SWAP")],
        "/api/v5/market/history-candles",
        &[],
    ),
    public(
        "get_trades_history",
        &[("instId", "BTC-USDT-SWAP")],
        "/api/v5/market/history-trades",
        &[],
    ),
    post(
        "amend_spread_order",
        &[("ordId", "1"), ("newPx", "-0.5")],
        "/api/v5/sprd/amend-order",
        &[],
    ),
    public(
        "get_estimated_delivery_price",
        &[("instId", "BTC-USDT-SWAP")],
        "/api/v5/public/estimated-price",
        &[],
    ),
    public(
        "get_discount_rates",
        &[],
        "/api/v5/public/discount-rate-interest-free-quota",
        &[],
    ),
    public(
        "convert_contract_coin",
        &[("instId", "BTC-USDT-SWAP"), ("sz", "1")],
        "/api/v5/public/convert-contract-coin",
        &[],
    ),
    public(
        "get_index_tickers",
        &[("quoteCcy", "USDT")],
        "/api/v5/market/index-tickers",
        &[],
    ),
    public(
        "get_mark_price_candles",
        &[("instId", "BTC-USDT-SWAP")],
        "/api/v5/market/mark-price-candles",
        &[],
    ),
    get(
        "get_asset_bill_history",
        &[],
        "/api/v5/asset/bills-history",
        &[],
    ),
    get(
        "get_convert_currency_pair",
        &[("fromCcy", "USDT"), ("toCcy", "BTC")],
        "/api/v5/asset/convert/currency-pair",
        &[],
    ),
    post(
        "estimate_convert_quote",
        &[
            ("baseCcy", "BTC"),
            ("quoteCcy", "USDT"),
            ("side", "buy"),
            ("rfqSz", "1"),
            ("rfqSzCcy", "BTC"),
        ],
        "/api/v5/asset/convert/estimate-quote",
        &[],
    ),
    post(
        "execute_convert_trade",
        &[
            ("quoteId", "quote1"),
            ("baseCcy", "BTC"),
            ("quoteCcy", "USDT"),
            ("side", "buy"),
            ("sz", "1"),
            ("szCcy", "BTC"),
        ],
        "/api/v5/asset/convert/trade",
        &[],
    ),
    public("get_system_status", &[], "/api/v5/system/status", &[]),
    public(
        "get_price_limit",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "/api/v5/public/price-limit",
        &[],
    ),
    public(
        "get_mark_price",
        &[("instType", "SWAP")],
        "/api/v5/public/mark-price",
        &[],
    ),
    post(
        "place_algo_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("tdMode", "cross"),
            ("side", "sell"),
            ("ordType", "conditional"),
            ("sz", "1"),
            ("slTriggerPx", "50000"),
            ("slOrdPx", "-1"),
            ("reduceOnly", "true"),
        ],
        "/api/v5/trade/order-algo",
        &[],
    ),
    post(
        "amend_algo_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("algoId", "42"),
            ("newSlTriggerPx", "49000"),
            ("cxlOnFail", "true"),
        ],
        "/api/v5/trade/amend-algos",
        &[],
    ),
    post(
        "cancel_algo_orders",
        &[(
            "orders",
            "[{\"instId\":\"BTC-USDT-SWAP\",\"algoId\":\"42\"}]",
        )],
        "/api/v5/trade/cancel-algos",
        &[],
    ),
    get(
        "get_algo_order",
        &[("algoId", "42")],
        "/api/v5/trade/order-algo",
        &[],
    ),
    get(
        "get_pending_algo_orders",
        &[("ordType", "conditional,oco")],
        "/api/v5/trade/orders-algo-pending",
        &[],
    ),
    get(
        "get_algo_order_history",
        &[("ordType", "trigger"), ("state", "effective")],
        "/api/v5/trade/orders-algo-history",
        &[],
    ),
    post(
        "adjust_position_margin",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("posSide", "net"),
            ("type", "add"),
            ("amt", "1"),
        ],
        "/api/v5/account/position/margin-balance",
        &[],
    ),
    // Order book trading: market data.
    public(
        "get_candles_ticks",
        &[SWAP, ("bar", "1m")],
        "/api/v5/market/candles",
        &["instId=BTC-USDT-SWAP", "bar=1m"],
    ),
    public(
        "get_orderbook",
        &[SWAP, ("sz", "5")],
        "/api/v5/market/books",
        &["instId=BTC-USDT-SWAP", "sz=5"],
    ),
    public(
        "get_tickers",
        &[("instType", "SWAP")],
        "/api/v5/market/tickers",
        &["instType=SWAP"],
    ),
    public(
        "get_public_trades",
        &[SWAP, ("limit", "10")],
        "/api/v5/market/trades",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_option_family_trades",
        &[("instFamily", "BTC-USD")],
        "/api/v5/market/option/instrument-family-trades",
        &["instFamily=BTC-USD"],
    ),
    // Public data.
    public(
        "get_public_instruments",
        &[("instType", "SPOT")],
        "/api/v5/public/instruments",
        &["instType=SPOT"],
    ),
    public(
        "get_public_underlying",
        &[("instType", "SWAP")],
        "/api/v5/public/underlying",
        &["instType=SWAP"],
    ),
    public(
        "get_funding_rate",
        &[SWAP],
        "/api/v5/public/funding-rate",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_funding_rate_history",
        &[SWAP, ("limit", "5")],
        "/api/v5/public/funding-rate-history",
        &["instId=BTC-USDT-SWAP", "limit=5"],
    ),
    public(
        "get_open_interest",
        &[("instType", "SWAP")],
        "/api/v5/public/open-interest",
        &["instType=SWAP"],
    ),
    public(
        "get_position_tiers",
        &[("instType", "SWAP"), ("tdMode", "cross"), SWAP],
        "/api/v5/public/position-tiers",
        &["tdMode=cross", "instFamily=BTC-USDT"],
    ),
    public(
        "get_delivery_exercise_history",
        &[("instType", "OPTION"), ("instFamily", "BTC-USD")],
        "/api/v5/public/delivery-exercise-history",
        &["instType=OPTION"],
    ),
    public(
        "get_option_summary",
        &[("instFamily", "BTC-USD")],
        "/api/v5/public/opt-summary",
        &["instFamily=BTC-USD"],
    ),
    public(
        "get_option_tick_bands",
        &[("instType", "OPTION")],
        "/api/v5/public/instrument-tick-bands",
        &["instType=OPTION"],
    ),
    public(
        "get_option_trades",
        &[("instFamily", "BTC-USD")],
        "/api/v5/public/option-trades",
        &["instFamily=BTC-USD"],
    ),
    // Trading statistics (rubik).
    public(
        "get_trading_data_support_coin",
        &[],
        "/api/v5/rubik/stat/trading-data/support-coin",
        &[],
    ),
    public(
        "get_taker_volume",
        &[("ccy", "BTC"), ("instType", "SPOT")],
        "/api/v5/rubik/stat/taker-volume",
        &["ccy=BTC", "instType=SPOT"],
    ),
    public(
        "get_contract_taker_volume",
        &[SWAP, ("period", "5m")],
        "/api/v5/rubik/stat/taker-volume-contract",
        &["instId=BTC-USDT-SWAP", "period=5m"],
    ),
    public(
        "get_long_short_ratio",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/contracts/long-short-account-ratio",
        &["ccy=BTC"],
    ),
    public(
        "get_contract_long_short_ratio",
        &[SWAP],
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_top_trader_long_short_account_ratio",
        &[SWAP],
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_top_trader_long_short_position_ratio",
        &[SWAP],
        "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_contracts_open_interest_and_volume",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/contracts/open-interest-volume",
        &["ccy=BTC"],
    ),
    public(
        "get_contract_open_interest_history",
        &[SWAP],
        "/api/v5/rubik/stat/contracts/open-interest-history",
        &["instId=BTC-USDT-SWAP"],
    ),
    public(
        "get_options_open_interest_and_volume",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/option/open-interest-volume",
        &["ccy=BTC"],
    ),
    public(
        "get_option_put_call_ratio",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/option/open-interest-volume-ratio",
        &["ccy=BTC"],
    ),
    public(
        "get_option_open_interest_and_volume_by_expiry",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/option/open-interest-volume-expiry",
        &["ccy=BTC"],
    ),
    public(
        "get_option_open_interest_and_volume_by_strike",
        &[("ccy", "BTC"), ("expTime", "20261225")],
        "/api/v5/rubik/stat/option/open-interest-volume-strike",
        &["expTime=20261225"],
    ),
    public(
        "get_option_taker_block_volume",
        &[("ccy", "BTC")],
        "/api/v5/rubik/stat/option/taker-block-volume",
        &["ccy=BTC"],
    ),
    // Public financial product data.
    public(
        "get_public_borrow_info",
        &[("ccy", "USDT")],
        "/api/v5/finance/savings/lending-rate-summary",
        &["ccy=USDT"],
    ),
    public(
        "get_public_borrow_history",
        &[("ccy", "USDT")],
        "/api/v5/finance/savings/lending-rate-history",
        &["ccy=USDT"],
    ),
    public(
        "get_eth_staking_apy_history",
        &[("days", "7")],
        "/api/v5/finance/staking-defi/eth/apy-history",
        &["days=7"],
    ),
    public(
        "get_sol_staking_apy_history",
        &[("days", "7")],
        "/api/v5/finance/staking-defi/sol/apy-history",
        &["days=7"],
    ),
    // Spread trading public data.
    public(
        "get_spread_spreads",
        &[("baseCcy", "BTC")],
        "/api/v5/sprd/spreads",
        &["baseCcy=BTC"],
    ),
    public(
        "get_spread_books",
        &[SPRD],
        "/api/v5/sprd/books",
        &["sprdId=BTC-USDT_BTC-USDT-SWAP"],
    ),
    public(
        "get_spread_ticker",
        &[SPRD],
        "/api/v5/market/sprd-ticker",
        &["sprdId="],
    ),
    public(
        "get_spread_public_trades",
        &[SPRD],
        "/api/v5/sprd/public-trades",
        &["sprdId="],
    ),
    public(
        "get_spread_candles",
        &[SPRD, ("bar", "1m")],
        "/api/v5/market/sprd-candles",
        &["bar=1m"],
    ),
    public(
        "get_spread_history_candles",
        &[SPRD, ("bar", "1m")],
        "/api/v5/market/sprd-history-candles",
        &["bar=1m"],
    ),
    // Order book trading: trade.
    post(
        "place_order",
        &[
            SWAP,
            ("tdMode", "cross"),
            ("side", "buy"),
            ("ordType", "limit"),
            ("sz", "1"),
            ("px", "100"),
            ("clOrdId", "c1"),
        ],
        "/api/v5/trade/order",
        &[
            r#""instId":"BTC-USDT-SWAP""#,
            r#""side":"buy""#,
            r#""ordType":"limit""#,
            r#""px":"100""#,
            r#""clOrdId":"c1""#,
        ],
    ),
    post(
        "place_market_order",
        &[SWAP, ("tdMode", "cross"), ("side", "sell"), ("sz", "1")],
        "/api/v5/trade/order",
        &[r#""ordType":"market""#, r#""side":"sell""#],
    ),
    post(
        "place_market_buy_order",
        &[SWAP, ("tdMode", "cross"), ("sz", "1")],
        "/api/v5/trade/order",
        &[r#""ordType":"market""#, r#""side":"buy""#],
    ),
    post(
        "place_market_sell_order",
        &[SWAP, ("tdMode", "cross"), ("sz", "1")],
        "/api/v5/trade/order",
        &[r#""ordType":"market""#, r#""side":"sell""#],
    ),
    post(
        "place_limit_order",
        LIMIT_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"limit""#],
    ),
    post(
        "place_limit_buy_order",
        SIDED_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"limit""#, r#""side":"buy""#],
    ),
    post(
        "place_limit_sell_order",
        SIDED_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"limit""#, r#""side":"sell""#],
    ),
    post(
        "place_post_only_limit_order",
        LIMIT_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"post_only""#],
    ),
    post(
        "place_post_only_limit_buy_order",
        SIDED_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"post_only""#, r#""side":"buy""#],
    ),
    post(
        "place_post_only_limit_sell_order",
        SIDED_ORDER,
        "/api/v5/trade/order",
        &[r#""ordType":"post_only""#, r#""side":"sell""#],
    ),
    post(
        "pre_check_order",
        &[
            SWAP,
            ("tdMode", "cross"),
            ("side", "buy"),
            ("ordType", "limit"),
            ("sz", "1"),
            ("px", "1"),
        ],
        "/api/v5/trade/order-precheck",
        &[r#""instId":"BTC-USDT-SWAP""#],
    ),
    post(
        "place_batch_orders",
        &[(
            "orders",
            r#"[{"instId":"BTC-USDT-SWAP","tdMode":"cross","side":"buy","ordType":"limit","sz":"1","px":"1"}]"#,
        )],
        "/api/v5/trade/batch-orders",
        &[r#"[{"instId":"BTC-USDT-SWAP""#],
    ),
    post(
        "cancel_order",
        &[SWAP, ("ordId", "123")],
        "/api/v5/trade/cancel-order",
        &[r#""ordId":"123""#, r#""instId":"BTC-USDT-SWAP""#],
    ),
    post(
        "cancel_batch_orders",
        &[("orders", r#"[{"instId":"BTC-USDT-SWAP","ordId":"1"}]"#)],
        "/api/v5/trade/cancel-batch-orders",
        &[r#""ordId":"1""#],
    ),
    // With no pending orders the helper only lists orders and stops.
    get(
        "cancel_all_orders",
        &[SWAP],
        "/api/v5/trade/orders-pending",
        &["instId=BTC-USDT-SWAP", "limit=100"],
    ),
    post(
        "amend_order",
        &[SWAP, ("ordId", "123"), ("newPx", "101")],
        "/api/v5/trade/amend-order",
        &[r#""newPx":"101""#, r#""ordId":"123""#],
    ),
    post(
        "amend_multiple_orders",
        &[(
            "orders",
            r#"[{"instId":"BTC-USDT-SWAP","ordId":"1","newSz":"2"}]"#,
        )],
        "/api/v5/trade/amend-batch-orders",
        &[r#""newSz":"2""#],
    ),
    post(
        "close_positions",
        &[SWAP, ("mgnMode", "cross"), ("autoCxl", "true")],
        "/api/v5/trade/close-position",
        &[r#""mgnMode":"cross""#, r#""autoCxl":true"#],
    ),
    post(
        "set_cancel_all_after",
        &[("timeOut", "30")],
        "/api/v5/trade/cancel-all-after",
        &[r#""timeOut":"30""#],
    ),
    get(
        "get_order",
        &[SWAP, ("clOrdId", "c1")],
        "/api/v5/trade/order",
        &["instId=BTC-USDT-SWAP", "clOrdId=c1"],
    ),
    get(
        "get_order_list",
        &[("instType", "SWAP")],
        "/api/v5/trade/orders-pending",
        &["instType=SWAP"],
    ),
    get(
        "get_orders_history",
        &[("instType", "SWAP")],
        "/api/v5/trade/orders-history",
        &["instType=SWAP"],
    ),
    get(
        "get_orders_history_archive",
        &[("instType", "SWAP")],
        "/api/v5/trade/orders-history-archive",
        &["instType=SWAP"],
    ),
    get(
        "get_fills",
        &[("instType", "SWAP")],
        "/api/v5/trade/fills",
        &["instType=SWAP"],
    ),
    get(
        "get_fills_history",
        &[("instType", "SWAP")],
        "/api/v5/trade/fills-history",
        &["instType=SWAP"],
    ),
    get(
        "get_account_rate_limit",
        &[],
        "/api/v5/trade/account-rate-limit",
        &[],
    ),
    get(
        "get_easy_convert_currencies",
        &[("source", "1")],
        "/api/v5/trade/easy-convert-currency-list",
        &["source=1"],
    ),
    get(
        "get_easy_convert_history",
        &[("limit", "10")],
        "/api/v5/trade/easy-convert-history",
        &["limit=10"],
    ),
    post(
        "place_easy_convert",
        &[("fromCcy", r#"["ADA"]"#), ("toCcy", "USDT")],
        "/api/v5/trade/easy-convert",
        &[r#""fromCcy":["ADA"]"#, r#""toCcy":"USDT""#],
    ),
    // Spread trading.
    post(
        "place_spread_order",
        &[
            SPRD,
            ("side", "buy"),
            ("ordType", "limit"),
            ("sz", "1"),
            ("px", "1"),
        ],
        "/api/v5/sprd/order",
        &[r#""sprdId":"BTC-USDT_BTC-USDT-SWAP""#],
    ),
    post(
        "cancel_spread_order",
        &[("ordId", "1")],
        "/api/v5/sprd/cancel-order",
        &[r#""ordId":"1""#],
    ),
    post(
        "cancel_all_spread_orders",
        &[SPRD],
        "/api/v5/sprd/mass-cancel",
        &[r#""sprdId""#],
    ),
    get(
        "get_spread_order",
        &[("ordId", "1")],
        "/api/v5/sprd/order",
        &["ordId=1"],
    ),
    get(
        "get_spread_orders_pending",
        &[("limit", "5")],
        "/api/v5/sprd/orders-pending",
        &["limit=5"],
    ),
    get(
        "get_spread_orders_history",
        &[("limit", "5")],
        "/api/v5/sprd/orders-history",
        &["limit=5"],
    ),
    post(
        "set_spread_cancel_all_after",
        &[("timeOut", "10")],
        "/api/v5/sprd/cancel-all-after",
        &[r#""timeOut":"10""#],
    ),
    get(
        "get_spread_trades",
        &[("limit", "5")],
        "/api/v5/sprd/trades",
        &["limit=5"],
    ),
    // Trading account.
    get(
        "get_account_instruments",
        &[("instType", "SWAP")],
        "/api/v5/account/instruments",
        &["instType=SWAP"],
    ),
    get(
        "get_account_balance",
        &[("ccy", "BTC")],
        "/api/v5/account/balance",
        &["ccy=BTC"],
    ),
    get(
        "get_positions",
        &[("instType", "SWAP")],
        "/api/v5/account/positions",
        &["instType=SWAP"],
    ),
    get(
        "get_positions_history",
        &[("instType", "SWAP")],
        "/api/v5/account/positions-history",
        &["instType=SWAP"],
    ),
    get(
        "get_position_risk",
        &[("instType", "SWAP")],
        "/api/v5/account/account-position-risk",
        &["instType=SWAP"],
    ),
    get(
        "get_account_bills",
        &[("instType", "SWAP")],
        "/api/v5/account/bills",
        &["instType=SWAP"],
    ),
    get(
        "get_account_bills_archive",
        &[("instType", "SWAP")],
        "/api/v5/account/bills-archive",
        &["instType=SWAP"],
    ),
    get(
        "get_account_bills_history_archive",
        &[("year", "2026"), ("quarter", "Q1")],
        "/api/v5/account/bills-history-archive",
        &["year=2026", "quarter=Q1"],
    ),
    post(
        "post_account_bills_history_archive",
        &[("year", "2026"), ("quarter", "Q1")],
        "/api/v5/account/bills-history-archive",
        &[r#""quarter":"Q1""#],
    ),
    get("get_account_config", &[], "/api/v5/account/config", &[]),
    post(
        "set_position_mode",
        &[("posMode", "long_short_mode")],
        "/api/v5/account/set-position-mode",
        &[r#""posMode":"long_short_mode""#],
    ),
    post(
        "set_leverage",
        &[SWAP, ("lever", "5"), ("mgnMode", "cross")],
        "/api/v5/account/set-leverage",
        &[r#""lever":"5""#, r#""instId":"BTC-USDT-SWAP""#],
    ),
    get(
        "get_max_order_size",
        &[SWAP, ("tdMode", "cross")],
        "/api/v5/account/max-size",
        &["tdMode=cross", "instId=BTC-USDT-SWAP"],
    ),
    get(
        "get_max_avail_size",
        &[SWAP, ("tdMode", "cross")],
        "/api/v5/account/max-avail-size",
        &["tdMode=cross", "instId=BTC-USDT-SWAP"],
    ),
    get(
        "get_leverage",
        &[SWAP, ("mgnMode", "cross")],
        "/api/v5/account/leverage-info",
        &["mgnMode=cross", "instId=BTC-USDT-SWAP"],
    ),
    get(
        "get_adjust_leverage",
        &[
            ("instType", "SWAP"),
            ("mgnMode", "cross"),
            ("lever", "3"),
            SWAP,
        ],
        "/api/v5/account/adjust-leverage-info",
        &["lever=3"],
    ),
    get(
        "get_max_loan",
        &[SWAP, ("mgnMode", "cross")],
        "/api/v5/account/max-loan",
        &["mgnMode=cross"],
    ),
    get(
        "get_spot_fee_rates",
        &[],
        "/api/v5/account/trade-fee",
        &["instType=SPOT"],
    ),
    get(
        "get_margin_fee_rates",
        &[],
        "/api/v5/account/trade-fee",
        &["instType=MARGIN"],
    ),
    get(
        "get_swap_fee_rates",
        &[("instFamily", "BTC-USDT")],
        "/api/v5/account/trade-fee",
        &["instType=SWAP", "instFamily=BTC-USDT"],
    ),
    get(
        "get_futures_fee_rates",
        &[],
        "/api/v5/account/trade-fee",
        &["instType=FUTURES"],
    ),
    get(
        "get_option_fee_rates",
        &[],
        "/api/v5/account/trade-fee",
        &["instType=OPTION"],
    ),
    get(
        "get_interest_accrued",
        &[("ccy", "USDT")],
        "/api/v5/account/interest-accrued",
        &["ccy=USDT"],
    ),
    get(
        "get_interest_rate",
        &[("ccy", "USDT")],
        "/api/v5/account/interest-rate",
        &["ccy=USDT"],
    ),
    post(
        "set_greeks",
        &[("greeksType", "PA")],
        "/api/v5/account/set-greeks",
        &[r#""greeksType":"PA""#],
    ),
    get(
        "get_max_withdrawal",
        &[("ccy", "USDT")],
        "/api/v5/account/max-withdrawal",
        &["ccy=USDT"],
    ),
    get(
        "get_interest_limits",
        &[("ccy", "USDT")],
        "/api/v5/account/interest-limits",
        &["ccy=USDT"],
    ),
    post(
        "spot_manual_borrow_repay",
        &[("ccy", "USDT"), ("side", "repay"), ("amt", "1")],
        "/api/v5/account/spot-manual-borrow-repay",
        &[r#""side":"repay""#],
    ),
    post(
        "set_spot_auto_repay",
        &[("autoRepay", "false")],
        "/api/v5/account/set-auto-repay",
        &[r#""autoRepay":false"#],
    ),
    get(
        "get_spot_borrow_repay_history",
        &[("ccy", "USDT")],
        "/api/v5/account/spot-borrow-repay-history",
        &["ccy=USDT"],
    ),
    // Funding account.
    get(
        "get_currencies",
        &[("ccy", "BTC")],
        "/api/v5/asset/currencies",
        &[],
    ),
    get(
        "get_balances",
        &[("ccy", "BTC")],
        "/api/v5/asset/balances",
        &[],
    ),
    get(
        "get_asset_valuation",
        &[("ccy", "USDT")],
        "/api/v5/asset/asset-valuation",
        &["ccy=USDT"],
    ),
    post(
        "funds_transfer",
        &[
            ("ccy", "USDT"),
            ("amt", "1"),
            ("from_account", "FUND"),
            ("to_account", "TRADING"),
        ],
        "/api/v5/asset/transfer",
        &[r#""from":"6""#, r#""to":"18""#],
    ),
    get(
        "get_transfer_state",
        &[("transId", "1")],
        "/api/v5/asset/transfer-state",
        &["transId=1"],
    ),
    get(
        "get_bills",
        &[("ccy", "USDT")],
        "/api/v5/asset/bills",
        &["ccy=USDT"],
    ),
    get(
        "get_deposit_address",
        &[("ccy", "USDT")],
        "/api/v5/asset/deposit-address",
        &["ccy=USDT"],
    ),
    get(
        "get_deposit_history",
        &[("ccy", "USDT")],
        "/api/v5/asset/deposit-history",
        &["ccy=USDT"],
    ),
    get(
        "get_deposit_withdraw_status",
        &[("wdId", "1")],
        "/api/v5/asset/deposit-withdraw-status",
        &["wdId=1"],
    ),
    get("get_exchange_list", &[], "/api/v5/asset/exchange-list", &[]),
    post(
        "post_monthly_statement",
        &[("month", "Jan")],
        "/api/v5/asset/monthly-statement",
        &[r#""month":"Jan""#],
    ),
    get(
        "get_monthly_statement",
        &[("month", "Jan")],
        "/api/v5/asset/monthly-statement",
        &["month=Jan"],
    ),
    get(
        "get_convert_currencies",
        &[],
        "/api/v5/asset/convert/currencies",
        &[],
    ),
    get(
        "get_convert_history",
        &[("limit", "10")],
        "/api/v5/asset/convert/history",
        &["limit=10"],
    ),
    // Sub-account.
    get(
        "get_subaccount_list",
        &[("limit", "10")],
        "/api/v5/users/subaccount/list",
        &["limit=10"],
    ),
    get(
        "get_subaccount_trading_balance",
        &[("subAcct", "alpha")],
        "/api/v5/account/subaccount/balances",
        &["subAcct=alpha"],
    ),
    get(
        "get_subaccount_funding_balance",
        &[("subAcct", "alpha")],
        "/api/v5/asset/subaccount/balances",
        &["subAcct=alpha"],
    ),
    get(
        "get_subaccount_bills",
        &[("subAcct", "alpha")],
        "/api/v5/asset/subaccount/bills",
        &["subAcct=alpha"],
    ),
    post(
        "transfer_between_subaccounts",
        &[
            ("ccy", "USDT"),
            ("amt", "1"),
            ("fromSubAccount", "alpha"),
            ("toSubAccount", "beta"),
            ("from_account", "FUND"),
            ("to_account", "TRADING"),
        ],
        "/api/v5/asset/subaccount/transfer",
        &[
            r#""from":"6""#,
            r#""to":"18""#,
            r#""fromSubAccount":"alpha""#,
        ],
    ),
    get(
        "get_entrusted_subaccount_list",
        &[],
        "/api/v5/users/entrust-subaccount-list",
        &[],
    ),
    get(
        "get_subaccount_interest_limits",
        &[("subAcct", "alpha")],
        "/api/v5/account/subaccount/interest-limits",
        &["subAcct=alpha"],
    ),
    // Financial products: simple earn, staking, loans, dual investment, OKUSD.
    get(
        "get_saving_balance",
        &[("ccy", "USDT")],
        "/api/v5/finance/savings/balance",
        &["ccy=USDT"],
    ),
    post(
        "purchase_redeem_savings",
        &[("ccy", "USDT"), ("amt", "1"), ("side", "purchase")],
        "/api/v5/finance/savings/purchase-redempt",
        &[r#""side":"purchase""#],
    ),
    post(
        "set_savings_lending_rate",
        &[("ccy", "USDT"), ("rate", "0.01")],
        "/api/v5/finance/savings/set-lending-rate",
        &[r#""rate":"0.01""#],
    ),
    get(
        "get_savings_lending_history",
        &[("ccy", "USDT")],
        "/api/v5/finance/savings/lending-history",
        &["ccy=USDT"],
    ),
    post(
        "set_auto_earn",
        &[("ccy", "USDT"), ("action", "turn_on")],
        "/api/v5/account/set-auto-earn",
        &[r#""action":"turn_on""#],
    ),
    get(
        "get_staking_offers",
        &[("ccy", "ETH")],
        "/api/v5/finance/staking-defi/offers",
        &["ccy=ETH"],
    ),
    post(
        "purchase_staking",
        &[
            ("productId", "p1"),
            ("investData", r#"[{"ccy":"ETH","amt":"1"}]"#),
        ],
        "/api/v5/finance/staking-defi/purchase",
        &[r#""productId":"p1""#, r#""investData":[{"#],
    ),
    post(
        "redeem_staking",
        &[("ordId", "o1"), ("protocolType", "defi")],
        "/api/v5/finance/staking-defi/redeem",
        &[r#""ordId":"o1""#],
    ),
    post(
        "cancel_staking",
        &[("ordId", "o1"), ("protocolType", "defi")],
        "/api/v5/finance/staking-defi/cancel",
        &[r#""protocolType":"defi""#],
    ),
    get(
        "get_active_staking_orders",
        &[("ccy", "ETH")],
        "/api/v5/finance/staking-defi/orders-active",
        &["ccy=ETH"],
    ),
    get(
        "get_staking_order_history",
        &[("ccy", "ETH")],
        "/api/v5/finance/staking-defi/orders-history",
        &["ccy=ETH"],
    ),
    get(
        "get_eth_staking_product_info",
        &[],
        "/api/v5/finance/staking-defi/eth/product-info",
        &[],
    ),
    post(
        "purchase_eth_staking",
        &[("amt", "1")],
        "/api/v5/finance/staking-defi/eth/purchase",
        &[r#""amt":"1""#],
    ),
    post(
        "redeem_eth_staking",
        &[("amt", "1")],
        "/api/v5/finance/staking-defi/eth/redeem",
        &[r#""amt":"1""#],
    ),
    post(
        "cancel_eth_staking_redemption",
        &[("ordId", "o1")],
        "/api/v5/finance/staking-defi/eth/cancel-redeem",
        &[r#""ordId":"o1""#],
    ),
    get(
        "get_eth_staking_balance",
        &[],
        "/api/v5/finance/staking-defi/eth/balance",
        &[],
    ),
    get(
        "get_eth_staking_history",
        &[("type", "purchase")],
        "/api/v5/finance/staking-defi/eth/purchase-redeem-history",
        &["type=purchase"],
    ),
    get(
        "get_sol_staking_product_info",
        &[],
        "/api/v5/finance/staking-defi/sol/product-info",
        &[],
    ),
    post(
        "purchase_sol_staking",
        &[("amt", "1")],
        "/api/v5/finance/staking-defi/sol/purchase",
        &[r#""amt":"1""#],
    ),
    post(
        "redeem_sol_staking",
        &[("amt", "1")],
        "/api/v5/finance/staking-defi/sol/redeem",
        &[r#""amt":"1""#],
    ),
    get(
        "get_sol_staking_balance",
        &[],
        "/api/v5/finance/staking-defi/sol/balance",
        &[],
    ),
    get(
        "get_sol_staking_history",
        &[("type", "redeem")],
        "/api/v5/finance/staking-defi/sol/purchase-redeem-history",
        &["type=redeem"],
    ),
    get(
        "get_flexible_loan_borrow_currencies",
        &[],
        "/api/v5/finance/flexible-loan/borrow-currencies",
        &[],
    ),
    get(
        "get_flexible_loan_collateral_assets",
        &[("ccy", "BTC")],
        "/api/v5/finance/flexible-loan/collateral-assets",
        &["ccy=BTC"],
    ),
    post(
        "get_flexible_loan_max_loan",
        &[
            ("borrowCcy", "USDT"),
            ("supCollateral", r#"[{"ccy":"BTC","amt":"1"}]"#),
        ],
        "/api/v5/finance/flexible-loan/max-loan",
        &[r#""borrowCcy":"USDT""#],
    ),
    get(
        "get_flexible_loan_max_collateral_redeem",
        &[("ccy", "BTC")],
        "/api/v5/finance/flexible-loan/max-collateral-redeem-amount",
        &["ccy=BTC"],
    ),
    post(
        "adjust_flexible_loan_collateral",
        &[
            ("type", "add"),
            ("collateralCcy", "BTC"),
            ("collateralAmt", "1"),
        ],
        "/api/v5/finance/flexible-loan/adjust-collateral",
        &[r#""type":"add""#],
    ),
    get(
        "get_flexible_loan_info",
        &[("ordId", "o1")],
        "/api/v5/finance/flexible-loan/loan-info",
        &["ordId=o1"],
    ),
    get(
        "get_flexible_loan_history",
        &[("limit", "10")],
        "/api/v5/finance/flexible-loan/loan-history",
        &["limit=10"],
    ),
    get(
        "get_flexible_loan_interest_accrued",
        &[("ccy", "USDT")],
        "/api/v5/finance/flexible-loan/interest-accrued",
        &["ccy=USDT"],
    ),
    post(
        "borrow_flexible_loan",
        &[
            ("loanData", r#"[{"ccy":"USDT","amt":"10"}]"#),
            ("clOrdId", "c1"),
        ],
        "/api/v5/finance/flexible-loan/borrow",
        &[r#""clOrdId":"c1""#],
    ),
    post(
        "repay_flexible_loan",
        &[
            ("ordId", "o1"),
            ("ccy", "USDT"),
            ("amt", "1"),
            ("clOrdId", "c1"),
        ],
        "/api/v5/finance/flexible-loan/repay",
        &[r#""ordId":"o1""#],
    ),
    get(
        "get_flexible_loan_emode_info",
        &[],
        "/api/v5/finance/flexible-loan/emode-info",
        &[],
    ),
    get(
        "get_dual_investment_currency_pairs",
        &[],
        "/api/v5/finance/sfp/dcd/currency-pair",
        &[],
    ),
    get(
        "get_dual_investment_products",
        &[("baseCcy", "BTC"), ("quoteCcy", "USDT"), ("optType", "C")],
        "/api/v5/finance/sfp/dcd/products",
        &["baseCcy=BTC", "optType=C"],
    ),
    post(
        "request_dual_investment_quote",
        &[
            ("productId", "p1"),
            ("notionalSz", "10"),
            ("notionalCcy", "USDT"),
        ],
        "/api/v5/finance/sfp/dcd/quote",
        &[r#""productId":"p1""#],
    ),
    post(
        "trade_dual_investment",
        &[("quoteId", "q1")],
        "/api/v5/finance/sfp/dcd/trade",
        &[r#""quoteId":"q1""#],
    ),
    post(
        "request_dual_investment_redeem_quote",
        &[("ordId", "o1")],
        "/api/v5/finance/sfp/dcd/redeem-quote",
        &[r#""ordId":"o1""#],
    ),
    post(
        "redeem_dual_investment",
        &[("ordId", "o1"), ("quoteId", "q1")],
        "/api/v5/finance/sfp/dcd/redeem",
        &[r#""quoteId":"q1""#],
    ),
    get(
        "get_dual_investment_order_status",
        &[("ordId", "o1")],
        "/api/v5/finance/sfp/dcd/order-status",
        &["ordId=o1"],
    ),
    get(
        "get_dual_investment_order_history",
        &[("limit", "10")],
        "/api/v5/finance/sfp/dcd/order-history",
        &["limit=10"],
    ),
    get("get_okusd_limits", &[], "/api/v5/finance/okusd/limits", &[]),
    get(
        "get_okusd_account",
        &[],
        "/api/v5/finance/okusd/account",
        &[],
    ),
    get(
        "get_okusd_rate_history",
        &[("limit", "10")],
        "/api/v5/finance/okusd/rate/history",
        &["limit=10"],
    ),
    get(
        "get_okusd_subscribe_history",
        &[("limit", "10")],
        "/api/v5/finance/okusd/subscribe/history",
        &[],
    ),
    get(
        "get_okusd_redeem_history",
        &[("limit", "10")],
        "/api/v5/finance/okusd/redeem/history",
        &[],
    ),
    get(
        "get_okusd_rewards_history",
        &[("limit", "10")],
        "/api/v5/finance/okusd/rewards/history",
        &[],
    ),
    post(
        "subscribe_okusd",
        &[("amt", "10"), ("clOrdId", "c1")],
        "/api/v5/finance/okusd/subscribe",
        &[r#""amt":"10""#],
    ),
    post(
        "redeem_okusd",
        &[("amt", "10"), ("redeemType", "1"), ("clOrdId", "c1")],
        "/api/v5/finance/okusd/redeem",
        &[r#""clOrdId":"c1""#],
    ),
];

/// Accept one HTTP request, reply with an OKX success envelope and return the
/// raw request text (request line, headers and body).
fn server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .expect("timeout");
        let mut raw = Vec::new();
        let mut buffer = [0u8; 4096];
        loop {
            let size = stream.read(&mut buffer).expect("read");
            assert!(size > 0, "connection closed before request completed");
            raw.extend_from_slice(&buffer[..size]);
            let text = String::from_utf8_lossy(&raw);
            if let Some(split) = text.find("\r\n\r\n") {
                let length = text[..split]
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length:")
                            .and_then(|value| value.trim().parse::<usize>().ok())
                    })
                    .unwrap_or(0);
                if raw.len() >= split + 4 + length {
                    break;
                }
            }
        }
        let body = r#"{"code":"0","msg":"","data":[]}"#;
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            body.len(),
            body
        );
        stream.write_all(response.as_bytes()).expect("write");
        String::from_utf8_lossy(&raw).into_owned()
    });
    (format!("http://{address}"), handle)
}

fn client(base_url: String) -> OkxClient {
    OkxClient::with_base_url(
        Some("key".into()),
        Some("secret".into()),
        Some("pass".into()),
        "0".into(),
        Duration::from_secs(5),
        base_url,
    )
    .expect("client")
}

fn owned(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

async fn run_case(case: &Case) -> std::result::Result<(), String> {
    let (base_url, handle) = server();
    let client = client(base_url);
    let params = owned(case.params);
    let response = if case.public {
        client.public_request(case.name, params).await
    } else {
        client.private_request(case.name, params).await
    };
    let response = response.map_err(|error| format!("{}: request failed: {error}", case.name))?;
    if response.data["code"] != Value::String("0".into()) {
        return Err(format!(
            "{}: unexpected response {}",
            case.name, response.data
        ));
    }
    let request = handle
        .join()
        .map_err(|_| format!("{}: server thread panicked", case.name))?;
    let request_line = request.lines().next().unwrap_or_default().to_string();
    let target = request_line
        .strip_prefix(&format!("{} ", case.method))
        .ok_or_else(|| {
            format!(
                "{}: expected {} got `{request_line}`",
                case.name, case.method
            )
        })?
        .trim_end_matches(" HTTP/1.1");
    let (path, query) = target.split_once('?').unwrap_or((target, ""));
    if path != case.path {
        return Err(format!(
            "{}: expected path {} got {path}",
            case.name, case.path
        ));
    }
    let signed = request.to_ascii_lowercase().contains("ok-access-sign:");
    if signed == case.public {
        return Err(format!(
            "{}: expected signed={} got signed={signed}",
            case.name, !case.public
        ));
    }
    let body = request.split_once("\r\n\r\n").map_or("", |(_, body)| body);
    if case.method == "POST" {
        serde_json::from_str::<Value>(body)
            .map_err(|error| format!("{}: body is not JSON ({error}): {body}", case.name))?;
    }
    let haystack = if case.method == "GET" { query } else { body };
    for needle in case.expect {
        if !haystack.contains(needle) {
            return Err(format!(
                "{}: expected `{needle}` in `{haystack}`",
                case.name
            ));
        }
    }
    Ok(())
}

#[tokio::test]
async fn every_dispatch_name_hits_documented_route() {
    let mut failures = Vec::new();
    for case in CASES {
        if let Err(message) = run_case(case).await {
            failures.push(message);
        }
    }
    assert!(
        failures.is_empty(),
        "route failures:\n{}",
        failures.join("\n")
    );
}

#[test]
fn case_table_has_unique_names() {
    let mut names = CASES.iter().map(|case| case.name).collect::<Vec<_>>();
    names.sort_unstable();
    let before = names.len();
    names.dedup();
    assert_eq!(before, names.len(), "duplicate route case");
}

#[tokio::test]
async fn unknown_method_names_are_rejected_before_network() {
    let client = OkxClient::public(Duration::from_secs(1)).expect("client");
    let public = client
        .public_request("get_unknown_market_method", Vec::new())
        .await
        .expect_err("public");
    assert!(public.to_string().contains("unsupported OKX public method"));
    let private = client
        .private_request("place_unknown_private_method", Vec::new())
        .await
        .expect_err("private");
    assert!(
        private
            .to_string()
            .contains("unsupported OKX private method")
    );
}

#[tokio::test]
async fn trading_validations_fail_before_network() {
    let client = OkxClient::public(Duration::from_secs(1)).expect("client");
    let cases: &[(&str, &[(&str, &str)], &str)] = &[
        ("cancel_order", &[SWAP], "ordId"),
        ("get_order", &[SWAP], "ordId"),
        (
            "place_order",
            &[SWAP, ("tdMode", "cross"), ("side", "buy"), ("sz", "1")],
            "ordType",
        ),
        ("set_cancel_all_after", &[], "timeOut"),
        (
            "spot_manual_borrow_repay",
            &[("ccy", "USDT"), ("side", "loan"), ("amt", "1")],
            "borrow or repay",
        ),
        ("set_spot_auto_repay", &[], "autoRepay"),
        ("set_spread_cancel_all_after", &[("timeOut", "121")], "120"),
        ("place_batch_orders", &[("orders", "{}")], "array"),
    ];
    for (name, params, fragment) in cases {
        let error = client
            .private_request(name, owned(params))
            .await
            .expect_err(name);
        assert!(
            error.to_string().contains(fragment),
            "{name}: unexpected error {error}"
        );
    }
}

#[tokio::test]
async fn market_buy_helper_forces_side_and_type_over_caller_values() {
    let (base_url, handle) = server();
    client(base_url)
        .private_request(
            "place_market_buy_order",
            owned(&[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("tdMode", "cash"),
                ("side", "sell"),
                ("ordType", "limit"),
                ("sz", "1"),
            ]),
        )
        .await
        .expect("response");
    let request = handle.join().expect("server");
    let body: Value =
        serde_json::from_str(request.split_once("\r\n\r\n").expect("body").1).expect("json");
    assert_eq!(body["side"], "buy");
    assert_eq!(body["ordType"], "market");
    assert_eq!(body["instId"], "BTC-USDT");
}
