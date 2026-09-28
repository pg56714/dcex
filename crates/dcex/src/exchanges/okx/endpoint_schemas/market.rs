//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_server_time" => RiskEndpoint {
            path: "/api/v5/public/time",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_ticker" => RiskEndpoint {
            path: "/api/v5/market/ticker",
            post: false,
            public: true,
            keys: &["instId", "product_symbol"],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_full_orderbook" => RiskEndpoint {
            path: "/api/v5/market/books-full",
            post: false,
            public: true,
            keys: &["instId", "sz", "product_symbol"],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_candles_history" => RiskEndpoint {
            path: "/api/v5/market/history-candles",
            post: false,
            public: true,
            keys: &[
                "instId",
                "after",
                "before",
                "bar",
                "limit",
                "adjust",
                "product_symbol",
            ],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_trades_history" => RiskEndpoint {
            path: "/api/v5/market/history-trades",
            post: false,
            public: true,
            keys: &[
                "instId",
                "type",
                "after",
                "before",
                "limit",
                "product_symbol",
            ],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_estimated_delivery_price" => RiskEndpoint {
            path: "/api/v5/public/estimated-price",
            post: false,
            public: true,
            keys: &["instId", "product_symbol"],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_discount_rates" => RiskEndpoint {
            path: "/api/v5/public/discount-rate-interest-free-quota",
            post: false,
            public: true,
            keys: &["ccy"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_index_tickers" => RiskEndpoint {
            path: "/api/v5/market/index-tickers",
            post: false,
            public: true,
            keys: &["quoteCcy", "instId", "product_symbol"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_mark_price_candles" => RiskEndpoint {
            path: "/api/v5/market/mark-price-candles",
            post: false,
            public: true,
            keys: &[
                "instId",
                "after",
                "before",
                "bar",
                "limit",
                "product_symbol",
            ],
            required: &["instId"],
            bools: &[],
            schema: None,
        },
        "get_system_status" => RiskEndpoint {
            path: "/api/v5/system/status",
            post: false,
            public: true,
            keys: &["state"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "set_settlement_currency" => RiskEndpoint {
            path: "/api/v5/account/set-settle-currency",
            post: true,
            public: false,
            keys: &["settleCcy"],
            required: &["settleCcy"],
            bools: &[],
            schema: None,
        },
        "get_books_rpi" => RiskEndpoint {
            path: "/api/v5/market/books-rpi",
            post: false,
            public: true,
            keys: &["instId", "sz"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"sz\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-24h-total-volume
        "get_platform_24_volume" => RiskEndpoint {
            path: "/api/v5/market/platform-24-volume",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-call-auction-details
        "get_call_auction_details" => RiskEndpoint {
            path: "/api/v5/market/call-auction-details",
            post: false,
            public: true,
            keys: &["instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-create-rfq
        "get_block_tickers" => RiskEndpoint {
            path: "/api/v5/market/block-tickers",
            post: false,
            public: true,
            keys: &["instType", "instFamily"],
            required: &["instType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\"},\"instFamily\":{\"type\":\"string\"}},\"required\":[\"instType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-ticker
        "get_block_ticker" => RiskEndpoint {
            path: "/api/v5/market/block-ticker",
            post: false,
            public: true,
            keys: &["instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-public-multi-leg-transactions-of-block-trades
        "get_estimated_settlement_info" => RiskEndpoint {
            path: "/api/v5/public/estimated-settlement-info",
            post: false,
            public: true,
            keys: &["instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-futures-settlement-history
        "get_settlement_history" => RiskEndpoint {
            path: "/api/v5/public/settlement-history",
            post: false,
            public: true,
            keys: &["instFamily", "after", "before", "limit"],
            required: &["instFamily"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instFamily\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instFamily\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-security-fund
        "get_insurance_fund" => RiskEndpoint {
            path: "/api/v5/public/insurance-fund",
            post: false,
            public: true,
            keys: &[
                "instType",
                "type",
                "instFamily",
                "ccy",
                "before",
                "after",
                "limit",
            ],
            required: &["instType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\"},\"type\":{\"type\":\"string\"},\"instFamily\":{\"type\":\"string\"},\"ccy\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-premium-history
        "get_premium_history" => RiskEndpoint {
            path: "/api/v5/public/premium-history",
            post: false,
            public: true,
            keys: &["instId", "after", "before", "limit"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks
        "get_index_candles" => RiskEndpoint {
            path: "/api/v5/market/index-candles",
            post: false,
            public: true,
            keys: &["instId", "after", "before", "bar", "limit"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"bar\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks-history
        "get_history_index_candles" => RiskEndpoint {
            path: "/api/v5/market/history-index-candles",
            post: false,
            public: true,
            keys: &["instId", "after", "before", "bar", "limit"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"bar\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price-candlesticks-history
        "get_history_mark_price_candles" => RiskEndpoint {
            path: "/api/v5/market/history-mark-price-candles",
            post: false,
            public: true,
            keys: &["instId", "after", "before", "bar", "limit"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"bar\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-exchange-rate
        "get_exchange_rate" => RiskEndpoint {
            path: "/api/v5/market/exchange-rate",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-components
        "get_index_components" => RiskEndpoint {
            path: "/api/v5/market/index-components",
            post: false,
            public: true,
            keys: &["index"],
            required: &["index"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"index\":{\"type\":\"string\"}},\"required\":[\"index\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-economic-calendar-data
        "get_economic_calendar" => RiskEndpoint {
            path: "/api/v5/public/economic-calendar",
            post: false,
            public: true,
            keys: &["region", "importance", "before", "after", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"region\":{\"type\":\"string\"},\"importance\":{\"type\":\"string\"},\"before\":{\"type\":\"string\"},\"after\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-historical-market-data
        "get_market_data_history" => RiskEndpoint {
            path: "/api/v5/public/market-data-history",
            post: false,
            public: true,
            keys: &[
                "module",
                "instType",
                "instIdList",
                "instFamilyList",
                "dateAggrType",
                "begin",
                "end",
            ],
            required: &["module", "instType", "dateAggrType", "begin", "end"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"module\":{\"type\":\"string\"},\"instType\":{\"type\":\"string\"},\"instIdList\":{\"type\":\"string\"},\"instFamilyList\":{\"type\":\"string\"},\"dateAggrType\":{\"type\":\"string\"},\"begin\":{\"type\":\"string\"},\"end\":{\"type\":\"string\"}},\"required\":[\"module\",\"instType\",\"dateAggrType\",\"begin\",\"end\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-delta-hedge-currencies
        "get_delta_hedge_currencies" => RiskEndpoint {
            path: "/api/v5/public/delta-hedge-currencies",
            post: false,
            public: true,
            keys: &["ccy"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-margin-long-short-ratio
        "get_mm_instrument_types" => RiskEndpoint {
            path: "/api/v5/public/mm-instrument-types",
            post: false,
            public: true,
            keys: &["instType", "instId"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"instType":{"type":"string"},"instId":{"type":"string"}},"required":[]}"#,
            ),
        },
        _ => return None,
    })
}
