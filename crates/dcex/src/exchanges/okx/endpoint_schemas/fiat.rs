//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_fiat_deposit_payment_methods" => RiskEndpoint {
            path: "/api/v5/fiat/deposit-payment-methods",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Fiat currency, ISO-4217 3 digit currency code, e.g. TRY\"}},\"required\":[\"ccy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-payment-methods
        "get_fiat_withdrawal_payment_methods" => RiskEndpoint {
            path: "/api/v5/fiat/withdrawal-payment-methods",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Fiat currency, ISO-4217 3 digit currency code. e.g. TRY\"}},\"required\":[\"ccy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-order-history
        "get_fiat_withdrawal_order_history" => RiskEndpoint {
            path: "/api/v5/fiat/withdrawal-order-history",
            post: false,
            public: false,
            keys: &["ccy", "paymentMethod", "state", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Fiat currency, ISO-4217 3 digit currency code, e.g. TRY\"},\"paymentMethod\":{\"type\":\"string\",\"description\":\"Payment Method TR_BANKS PIX SEPA XPULSE NPP US_WIRE SG_FAST\"},\"state\":{\"type\":\"string\",\"description\":\"State of the order completed failed pending canceled inqueue processing\"},\"after\":{\"type\":\"string\",\"description\":\"Filter with a begin timestamp. Unix timestamp format in milliseconds (inclusive), e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Filter with an end timestamp. Unix timestamp format in milliseconds (inclusive), e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum and default is 100\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-order-detail
        "get_fiat_withdrawal" => RiskEndpoint {
            path: "/api/v5/fiat/withdrawal",
            post: false,
            public: false,
            keys: &["ordId"],
            required: &["ordId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ordId\":{\"type\":\"string\",\"description\":\"Order ID\"}},\"required\":[\"ordId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-order-history
        "get_fiat_deposit_order_history" => RiskEndpoint {
            path: "/api/v5/fiat/deposit-order-history",
            post: false,
            public: false,
            keys: &["ccy", "paymentMethod", "state", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"ISO-4217 3 digit currency code\"},\"paymentMethod\":{\"type\":\"string\",\"description\":\"Payment Method TR_BANKS PIX SEPA XPULSE NPP US_WIRE\"},\"state\":{\"type\":\"string\",\"description\":\"State of the order completed failed pending canceled inqueue processing\"},\"after\":{\"type\":\"string\",\"description\":\"Filter with a begin timestamp. Unix timestamp format in milliseconds (inclusive), e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Filter with an end timestamp. Unix timestamp format in milliseconds (inclusive), e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum and default is 100\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-order-detail
        "get_fiat_deposit" => RiskEndpoint {
            path: "/api/v5/fiat/deposit",
            post: false,
            public: false,
            keys: &["ordId"],
            required: &["ordId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ordId\":{\"type\":\"string\",\"description\":\"Order ID\"}},\"required\":[\"ordId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-currencies
        "get_fiat_buy_sell_currencies" => RiskEndpoint {
            path: "/api/v5/fiat/buy-sell/currencies",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-currency-pair
        "get_fiat_buy_sell_currency_pair" => RiskEndpoint {
            path: "/api/v5/fiat/buy-sell/currency-pair",
            post: false,
            public: false,
            keys: &["fromCcy", "toCcy"],
            required: &["fromCcy", "toCcy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"fromCcy\":{\"type\":\"string\",\"description\":\"Currency to sell, e.g. USD\"},\"toCcy\":{\"type\":\"string\",\"description\":\"Currency to buy, e.g. BTC\"}},\"required\":[\"fromCcy\",\"toCcy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-quote
        "fiat_buy_sell_quote" => RiskEndpoint {
            path: "/api/v5/fiat/buy-sell/quote",
            post: true,
            public: false,
            keys: &["side", "fromCcy", "toCcy", "rfqAmt", "rfqCcy"],
            required: &["side", "fromCcy", "toCcy", "rfqAmt", "rfqCcy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"side\":{\"type\":\"string\",\"description\":\"Side buy : Buy Crypto / Fiat with Fiat sell : Sell Crypto to Crypto / Fiat\"},\"fromCcy\":{\"type\":\"string\",\"description\":\"Currency to sell\"},\"toCcy\":{\"type\":\"string\",\"description\":\"Currency to buy\"},\"rfqAmt\":{\"type\":\"string\",\"description\":\"RFQ amount\"},\"rfqCcy\":{\"type\":\"string\",\"description\":\"RFQ currency\"}},\"required\":[\"side\",\"fromCcy\",\"toCcy\",\"rfqAmt\",\"rfqCcy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-buy-sell-trade
        "fiat_buy_sell_trade" => RiskEndpoint {
            path: "/api/v5/fiat/buy-sell/trade",
            post: true,
            public: false,
            keys: &[
                "quoteId",
                "side",
                "fromCcy",
                "toCcy",
                "rfqAmt",
                "rfqCcy",
                "paymentMethod",
                "clOrdId",
            ],
            required: &[
                "quoteId",
                "side",
                "fromCcy",
                "toCcy",
                "rfqAmt",
                "rfqCcy",
                "paymentMethod",
                "clOrdId",
            ],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"quoteId\":{\"type\":\"string\",\"description\":\"Quote ID Get from Buy/Sell quote API\"},\"side\":{\"type\":\"string\",\"description\":\"Side buy : Buy Crypto / Fiat with Fiat sell : Sell Crypto to Crypto / Fiat Should be the same as the Quote request\"},\"fromCcy\":{\"type\":\"string\",\"description\":\"Currency to sell Should be the same as the Quote request\"},\"toCcy\":{\"type\":\"string\",\"description\":\"Currency to buy Should be the same as the Quote request\"},\"rfqAmt\":{\"type\":\"string\",\"description\":\"RFQ amount Should be the same as the Quote request\"},\"rfqCcy\":{\"type\":\"string\",\"description\":\"RFQ currency Should be the same as the Quote request\"},\"paymentMethod\":{\"type\":\"string\",\"description\":\"paymentMethod balance\"},\"clOrdId\":{\"type\":\"string\",\"description\":\"Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.\"}},\"required\":[\"quoteId\",\"side\",\"fromCcy\",\"toCcy\",\"rfqAmt\",\"rfqCcy\",\"paymentMethod\",\"clOrdId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-trade-history
        "get_fiat_buy_sell_history" => RiskEndpoint {
            path: "/api/v5/fiat/buy-sell/history",
            post: false,
            public: false,
            keys: &["ordId", "clOrdId", "state", "begin", "end", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ordId\":{\"type\":\"string\",\"description\":\"Order ID\"},\"clOrdId\":{\"type\":\"string\",\"description\":\"Client Order ID as assigned by the client A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.\"},\"state\":{\"type\":\"string\",\"description\":\"Trade state processing completed failed\"},\"begin\":{\"type\":\"string\",\"description\":\"Filter with a begin timestamp. Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"end\":{\"type\":\"string\",\"description\":\"Filter with an end timestamp. Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-sub-account-maximum-withdrawals
        "create_fiat_withdrawal" => RiskEndpoint {
            path: "/api/v5/fiat/create-withdrawal",
            post: true,
            public: false,
            keys: &["paymentAcctId", "ccy", "amt", "paymentMethod", "clientId"],
            required: &["paymentAcctId", "ccy", "amt", "paymentMethod", "clientId"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"paymentAcctId":{"type":"string"},"ccy":{"type":"string"},"amt":{"type":"string"},"paymentMethod":{"type":"string"},"clientId":{"type":"string"}},"required":["paymentAcctId","ccy","amt","paymentMethod","clientId"]}"#,
            ),
        },
        "cancel_fiat_withdrawal" => RiskEndpoint {
            path: "/api/v5/fiat/cancel-withdrawal",
            post: true,
            public: false,
            keys: &["ordId"],
            required: &["ordId"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"ordId":{"type":"string"}},"required":["ordId"]}"#,
            ),
        },
        _ => return None,
    })
}
