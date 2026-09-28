//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "rfq_create_rfq" => RiskEndpoint {
            path: "/api/v5/rfq/create-rfq",
            post: true,
            public: false,
            keys: &[
                "counterparties",
                "anonymous",
                "clRfqId",
                "tag",
                "allowPartialExecution",
                "legs",
                "acctAlloc",
            ],
            required: &["counterparties", "legs"],
            bools: &["anonymous", "allowPartialExecution"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"counterparties\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"properties\":{},\"required\":[]}},\"anonymous\":{\"type\":\"boolean\"},\"clRfqId\":{\"type\":\"string\"},\"tag\":{\"type\":\"string\"},\"allowPartialExecution\":{\"type\":\"boolean\"},\"legs\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"tdMode\":{\"type\":\"string\"},\"ccy\":{\"type\":\"string\"},\"sz\":{\"type\":\"string\"},\"lmtPx\":{\"type\":\"string\"},\"side\":{\"type\":\"string\"},\"posSide\":{\"type\":\"string\"},\"tgtCcy\":{\"type\":\"string\"},\"tradeQuoteCcy\":{\"type\":\"string\"}},\"required\":[\"instId\",\"sz\",\"side\"]}},\"acctAlloc\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"acct\":{\"type\":\"string\"},\"legs\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"sz\":{\"type\":\"string\"},\"instId\":{\"type\":\"string\"},\"tdMode\":{\"type\":\"string\"},\"ccy\":{\"type\":\"string\"},\"posSide\":{\"type\":\"string\"}},\"required\":[\"sz\",\"instId\"]}}},\"required\":[\"acct\",\"legs\"]}}},\"required\":[\"counterparties\",\"legs\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-counterparties
        "get_rfq_counterparties" => RiskEndpoint {
            path: "/api/v5/rfq/counterparties",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-rfq
        "rfq_cancel_rfq" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-rfq",
            post: true,
            public: false,
            keys: &["rfqId", "clRfqId"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqId\":{\"type\":\"string\"},\"clRfqId\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs
        "rfq_cancel_batch_rfqs" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-batch-rfqs",
            post: true,
            public: false,
            keys: &["rfqIds", "clRfqIds"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqIds\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"properties\":{},\"required\":[]}},\"clRfqIds\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"properties\":{},\"required\":[]}}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-all-rfqs
        "rfq_cancel_all_rfqs" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-all-rfqs",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-execute-quote
        "rfq_execute_quote" => RiskEndpoint {
            path: "/api/v5/rfq/execute-quote",
            post: true,
            public: false,
            keys: &["rfqId", "quoteId", "legs"],
            required: &["rfqId", "quoteId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqId\":{\"type\":\"string\"},\"quoteId\":{\"type\":\"string\"},\"legs\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"sz\":{\"type\":\"string\"}},\"required\":[\"instId\",\"sz\"]}}},\"required\":[\"rfqId\",\"quoteId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-rfqs
        "get_rfq_rfqs" => RiskEndpoint {
            path: "/api/v5/rfq/rfqs",
            post: false,
            public: false,
            keys: &["rfqId", "clRfqId", "state", "beginId", "endId", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqId\":{\"type\":\"string\"},\"clRfqId\":{\"type\":\"string\"},\"state\":{\"type\":\"string\"},\"beginId\":{\"type\":\"string\"},\"endId\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-quotes
        "get_rfq_quotes" => RiskEndpoint {
            path: "/api/v5/rfq/quotes",
            post: false,
            public: false,
            keys: &[
                "rfqId",
                "clRfqId",
                "quoteId",
                "clQuoteId",
                "state",
                "beginId",
                "endId",
                "limit",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqId\":{\"type\":\"string\"},\"clRfqId\":{\"type\":\"string\"},\"quoteId\":{\"type\":\"string\"},\"clQuoteId\":{\"type\":\"string\"},\"state\":{\"type\":\"string\"},\"beginId\":{\"type\":\"string\"},\"endId\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-trades
        "get_rfq_trades" => RiskEndpoint {
            path: "/api/v5/rfq/trades",
            post: false,
            public: false,
            keys: &[
                "rfqId",
                "clRfqId",
                "quoteId",
                "blockTdId",
                "clQuoteId",
                "beginId",
                "endId",
                "beginTs",
                "endTs",
                "limit",
                "isSuccessful",
            ],
            required: &[],
            bools: &["isSuccessful"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"rfqId\":{\"type\":\"string\"},\"clRfqId\":{\"type\":\"string\"},\"quoteId\":{\"type\":\"string\"},\"blockTdId\":{\"type\":\"string\"},\"clQuoteId\":{\"type\":\"string\"},\"beginId\":{\"type\":\"string\"},\"endId\":{\"type\":\"string\"},\"beginTs\":{\"type\":\"string\"},\"endTs\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"},\"isSuccessful\":{\"type\":\"boolean\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-tickers
        "get_rfq_public_trades" => RiskEndpoint {
            path: "/api/v5/rfq/public-trades",
            post: false,
            public: true,
            keys: &["beginId", "endId", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"beginId\":{\"type\":\"string\"},\"endId\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-public-single-leg-transactions-of-block-trades
        "create_rfq_quote" => RiskEndpoint {
            path: "/api/v5/rfq/create-quote",
            post: true,
            public: false,
            keys: &[
                "rfqId",
                "clQuoteId",
                "tag",
                "anonymous",
                "quoteSide",
                "expiresIn",
                "legs",
            ],
            required: &["rfqId", "quoteSide", "legs"],
            bools: &["anonymous"],
            schema: Some(
                r#"{"type":"object","properties":{"rfqId":{"type":"string"},"clQuoteId":{"type":"string"},"tag":{"type":"string"},"anonymous":{"type":"boolean"},"quoteSide":{"type":"string"},"expiresIn":{"type":"string"},"legs":{"type":"array","items":{"type":"object","properties":{"instId":{"type":"string"},"tdMode":{"type":"string"},"ccy":{"type":"string"},"sz":{"type":"string"},"px":{"type":"string"},"side":{"type":"string"},"posSide":{"type":"string"},"tgtCcy":{"type":"string"},"tradeQuoteCcy":{"type":"string"}},"required":["instId","sz","px","side"]}}},"required":["rfqId","quoteSide","legs"]}"#,
            ),
        },
        "cancel_rfq_quote" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-quote",
            post: true,
            public: false,
            keys: &["quoteId", "clQuoteId", "rfqId"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"quoteId":{"type":"string"},"clQuoteId":{"type":"string"},"rfqId":{"type":"string"}},"required":[]}"#,
            ),
        },
        "get_rfq_maker_instrument_settings" => RiskEndpoint {
            path: "/api/v5/rfq/maker-instrument-settings",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some(r#"{"type":"object","properties":{},"required":[]}"#),
        },
        "set_rfq_maker_instrument_settings" => RiskEndpoint {
            path: "/api/v5/rfq/maker-instrument-settings",
            post: true,
            public: false,
            keys: &["instType", "includeAll", "data"],
            required: &["instType", "data"],
            bools: &["includeAll"],
            schema: Some(
                r#"{"type":"object","properties":{"instType":{"type":"string"},"includeAll":{"type":"boolean"},"data":{"type":"array","items":{"type":"object","properties":{"instFamily":{"type":"string"},"instId":{"type":"string"},"maxBlockSz":{"type":"string"},"makerPxBand":{"type":"string"}},"required":[]}}},"required":["instType","data"]}"#,
            ),
        },
        "reset_rfq_mmp" => RiskEndpoint {
            path: "/api/v5/rfq/mmp-reset",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some(r#"{"type":"object","properties":{},"required":[]}"#),
        },
        "set_rfq_mmp_config" => RiskEndpoint {
            path: "/api/v5/rfq/mmp-config",
            post: true,
            public: false,
            keys: &["timeInterval", "frozenInterval", "countLimit"],
            required: &["timeInterval", "frozenInterval", "countLimit"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"timeInterval":{"type":"string"},"frozenInterval":{"type":"string"},"countLimit":{"type":"string"}},"required":["timeInterval","frozenInterval","countLimit"]}"#,
            ),
        },
        "get_rfq_mmp_config" => RiskEndpoint {
            path: "/api/v5/rfq/mmp-config",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some(r#"{"type":"object","properties":{},"required":[]}"#),
        },
        "cancel_rfq_batch_quotes" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-batch-quotes",
            post: true,
            public: false,
            keys: &["quoteIds", "clQuoteIds"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"quoteIds":{"type":"array","items":{"type":"string"}},"clQuoteIds":{"type":"array","items":{"type":"string"}}},"required":[]}"#,
            ),
        },
        "cancel_all_rfq_quotes" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-all-quotes",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some(r#"{"type":"object","properties":{},"required":[]}"#),
        },
        "set_rfq_cancel_all_after" => RiskEndpoint {
            path: "/api/v5/rfq/cancel-all-after",
            post: true,
            public: false,
            keys: &["timeOut"],
            required: &["timeOut"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"timeOut":{"type":"string"}},"required":["timeOut"]}"#,
            ),
        },
        _ => return None,
    })
}
