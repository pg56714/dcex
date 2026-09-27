use super::RiskEndpoint;
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
        "set_isolated_mode" => RiskEndpoint {
            path: "/api/v5/account/set-isolated-mode",
            post: true,
            public: false,
            keys: &["isoMode", "type"],
            required: &["isoMode", "type"],
            bools: &[],
            schema: None,
        },
        "get_account_risk_state" => RiskEndpoint {
            path: "/api/v5/account/risk-state",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_greeks" => RiskEndpoint {
            path: "/api/v5/account/greeks",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_pm_position_tiers" => RiskEndpoint {
            path: "/api/v5/account/position-tiers",
            post: false,
            public: false,
            keys: &["instType", "instFamily"],
            required: &["instType", "instFamily"],
            bools: &[],
            schema: None,
        },
        "set_account_level" => RiskEndpoint {
            path: "/api/v5/account/set-account-level",
            post: true,
            public: false,
            keys: &["acctLv"],
            required: &["acctLv"],
            bools: &[],
            schema: None,
        },
        "get_collateral_assets" => RiskEndpoint {
            path: "/api/v5/account/collateral-assets",
            post: false,
            public: false,
            keys: &["ccy", "collateralEnabled"],
            required: &[],
            bools: &["collateralEnabled"],
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
        "amend_spread_order" => RiskEndpoint {
            path: "/api/v5/sprd/amend-order",
            post: true,
            public: false,
            keys: &["ordId", "clOrdId", "reqId", "newSz", "newPx"],
            required: &[],
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
        "convert_contract_coin" => RiskEndpoint {
            path: "/api/v5/public/convert-contract-coin",
            post: false,
            public: true,
            keys: &[
                "type",
                "instId",
                "sz",
                "px",
                "unit",
                "opType",
                "product_symbol",
            ],
            required: &["instId", "sz"],
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
        "get_asset_bill_history" => RiskEndpoint {
            path: "/api/v5/asset/bills-history",
            post: false,
            public: false,
            keys: &[
                "ccy",
                "type",
                "thirdPartyType",
                "clientId",
                "after",
                "before",
                "limit",
                "pagingType",
            ],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_convert_currency_pair" => RiskEndpoint {
            path: "/api/v5/asset/convert/currency-pair",
            post: false,
            public: false,
            keys: &["fromCcy", "toCcy", "convertMode"],
            required: &["fromCcy", "toCcy"],
            bools: &[],
            schema: None,
        },
        "estimate_convert_quote" => RiskEndpoint {
            path: "/api/v5/asset/convert/estimate-quote",
            post: true,
            public: false,
            keys: &[
                "baseCcy",
                "quoteCcy",
                "side",
                "rfqSz",
                "rfqSzCcy",
                "clQReqId",
                "convertMode",
            ],
            required: &["baseCcy", "quoteCcy", "side", "rfqSz", "rfqSzCcy"],
            bools: &[],
            schema: None,
        },
        "execute_convert_trade" => RiskEndpoint {
            path: "/api/v5/asset/convert/trade",
            post: true,
            public: false,
            keys: &[
                "quoteId",
                "baseCcy",
                "quoteCcy",
                "side",
                "sz",
                "szCcy",
                "clTReqId",
                "convertMode",
            ],
            required: &["quoteId", "baseCcy", "quoteCcy", "side", "sz", "szCcy"],
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
        "set_fee_type" => RiskEndpoint {
            path: "/api/v5/account/set-fee-type",
            post: true,
            public: false,
            keys: &["feeType"],
            required: &["feeType"],
            bools: &[],
            schema: None,
        },
        "set_risk_offset_amount" => RiskEndpoint {
            path: "/api/v5/account/set-riskOffset-amt",
            post: true,
            public: false,
            keys: &["ccy", "clSpotInUseAmt"],
            required: &["ccy", "clSpotInUseAmt"],
            bools: &[],
            schema: None,
        },
        "activate_options" => RiskEndpoint {
            path: "/api/v5/account/activate-option",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "set_auto_loan" => RiskEndpoint {
            path: "/api/v5/account/set-auto-loan",
            post: true,
            public: false,
            keys: &["autoLoan"],
            required: &[],
            bools: &["autoLoan"],
            schema: None,
        },
        "preset_account_level_switch" => RiskEndpoint {
            path: "/api/v5/account/account-level-switch-preset",
            post: true,
            public: false,
            keys: &["acctLv", "lever"],
            required: &["acctLv"],
            bools: &[],
            schema: None,
        },
        "precheck_account_level_switch" => RiskEndpoint {
            path: "/api/v5/account/set-account-switch-precheck",
            post: false,
            public: false,
            keys: &["acctLv"],
            required: &["acctLv"],
            bools: &[],
            schema: None,
        },
        "set_collateral_assets" => RiskEndpoint {
            path: "/api/v5/account/set-collateral-assets",
            post: true,
            public: false,
            keys: &["type", "collateralEnabled", "ccyList"],
            required: &["type", "collateralEnabled"],
            bools: &["collateralEnabled"],
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
        "set_trading_config" => RiskEndpoint {
            path: "/api/v5/account/set-trading-config",
            post: true,
            public: false,
            keys: &["type", "stgyType"],
            required: &["type"],
            bools: &[],
            schema: None,
        },
        "precheck_delta_neutral" => RiskEndpoint {
            path: "/api/v5/account/precheck-set-delta-neutral",
            post: false,
            public: false,
            keys: &["stgyType"],
            required: &["stgyType"],
            bools: &[],
            schema: None,
        },
        "get_repayment_currencies" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-currency-list-v2",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "repay_debt" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-v2",
            post: true,
            public: false,
            keys: &["debtCcy", "repayCcyList"],
            required: &["debtCcy", "repayCcyList"],
            bools: &[],
            schema: None,
        },
        "get_repayment_history" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-history-v2",
            post: false,
            public: false,
            keys: &["after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_spread_order_history_archive" => RiskEndpoint {
            path: "/api/v5/sprd/orders-history-archive",
            post: false,
            public: false,
            keys: &[
                "sprdId",
                "ordType",
                "state",
                "instType",
                "instFamily",
                "beginId",
                "endId",
                "begin",
                "end",
                "limit",
            ],
            required: &[],
            bools: &[],
            schema: None,
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bill-types
        "get_bill_types" => RiskEndpoint {
            path: "/api/v5/account/subtypes",
            post: false,
            public: false,
            keys: &["type"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-new
        "simulate_positions" => RiskEndpoint {
            path: "/api/v5/account/position-builder",
            post: true,
            public: false,
            keys: &[
                "acctLv",
                "inclRealPosAndEq",
                "lever",
                "simPos",
                "simAsset",
                "greeksType",
                "idxVol",
            ],
            required: &[],
            bools: &["inclRealPosAndEq"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"acctLv\":{\"type\":\"string\"},\"inclRealPosAndEq\":{\"type\":\"boolean\"},\"lever\":{\"type\":\"string\"},\"simPos\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"pos\":{\"type\":\"string\"},\"avgPx\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[\"instId\",\"pos\",\"avgPx\"]}},\"simAsset\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"amt\":{\"type\":\"string\"}},\"required\":[\"ccy\",\"amt\"]}},\"greeksType\":{\"type\":\"string\"},\"idxVol\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-trend-graph
        "get_position_margin_graph" => RiskEndpoint {
            path: "/api/v5/account/position-builder-graph",
            post: true,
            public: false,
            keys: &[
                "inclRealPosAndEq",
                "simPos",
                "simAsset",
                "type",
                "mmrConfig",
            ],
            required: &["type", "mmrConfig"],
            bools: &["inclRealPosAndEq"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"inclRealPosAndEq\":{\"type\":\"boolean\"},\"simPos\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"pos\":{\"type\":\"string\"},\"avgPx\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[\"instId\",\"pos\",\"avgPx\"]}},\"simAsset\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"amt\":{\"type\":\"string\"}},\"required\":[\"ccy\",\"amt\"]}},\"type\":{\"type\":\"string\"},\"mmrConfig\":{\"type\":\"object\",\"properties\":{\"acctLv\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[]}},\"required\":[\"type\",\"mmrConfig\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-move-positions
        "move_positions" => RiskEndpoint {
            path: "/api/v5/account/move-positions",
            post: true,
            public: false,
            keys: &["fromAcct", "toAcct", "legs", "clientId"],
            required: &["fromAcct", "toAcct", "legs", "clientId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"fromAcct\":{\"type\":\"string\"},\"toAcct\":{\"type\":\"string\"},\"legs\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"from\":{\"type\":\"object\",\"properties\":{\"posId\":{\"type\":\"string\"},\"sz\":{\"type\":\"string\"},\"side\":{\"type\":\"string\"}},\"required\":[\"posId\",\"sz\",\"side\"]},\"to\":{\"type\":\"object\",\"properties\":{\"tdMode\":{\"type\":\"string\"},\"posSide\":{\"type\":\"string\"},\"ccy\":{\"type\":\"string\"}},\"required\":[]}},\"required\":[\"from\",\"to\"]}},\"clientId\":{\"type\":\"string\"}},\"required\":[\"fromAcct\",\"toAcct\",\"legs\",\"clientId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-move-positions-history
        "get_move_positions_history" => RiskEndpoint {
            path: "/api/v5/account/move-positions-history",
            post: false,
            public: false,
            keys: &[
                "blockTdId",
                "clientId",
                "beginTs",
                "endTs",
                "limit",
                "state",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"blockTdId\":{\"type\":\"string\"},\"clientId\":{\"type\":\"string\"},\"beginTs\":{\"type\":\"string\"},\"endTs\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"},\"state\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-adjust-demo-account-balance
        "adjust_demo_balance" => RiskEndpoint {
            path: "/api/v5/account/demo-adjust-balance",
            post: true,
            public: false,
            keys: &["type", "adjustments"],
            required: &["type", "adjustments"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\"},\"adjustments\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"amt\":{\"type\":\"string\"}},\"required\":[\"ccy\",\"amt\"]}}},\"required\":[\"type\",\"adjustments\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-rpi-order-book
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
        "get_block_trades" => RiskEndpoint {
            path: "/api/v5/public/block-trades",
            post: false,
            public: true,
            keys: &["instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-estimated-future-settlement-price
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
        "get_loan_ratio" => RiskEndpoint {
            path: "/api/v5/rubik/stat/margin/loan-ratio",
            post: false,
            public: true,
            keys: &["ccy", "begin", "end", "period"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"begin\":{\"type\":\"string\"},\"end\":{\"type\":\"string\"},\"period\":{\"type\":\"string\"}},\"required\":[\"ccy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-non-tradable-assets
        "get_non_tradable_assets" => RiskEndpoint {
            path: "/api/v5/asset/non-tradable-assets",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-create-sub-account
        "create_sub_account" => RiskEndpoint {
            path: "/api/v5/users/subaccount/create-subaccount",
            post: true,
            public: false,
            keys: &["subAcct", "type", "label", "pwd"],
            required: &["subAcct", "type"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"type\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"pwd\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"type\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-create-an-api-key-for-a-sub-account
        "create_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/apikey",
            post: true,
            public: false,
            keys: &["subAcct", "label", "passphrase", "perm", "ip"],
            required: &["subAcct", "label", "passphrase"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"passphrase\":{\"type\":\"string\"},\"perm\":{\"type\":\"string\"},\"ip\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"label\",\"passphrase\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-query-the-api-key-of-a-sub-account
        "get_sub_account_api_keys" => RiskEndpoint {
            path: "/api/v5/users/subaccount/apikey",
            post: false,
            public: false,
            keys: &["subAcct", "apiKey"],
            required: &["subAcct"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"}},\"required\":[\"subAcct\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-reset-the-api-key-of-a-sub-account
        "modify_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/modify-apikey",
            post: true,
            public: false,
            keys: &["subAcct", "apiKey", "label", "perm", "ip"],
            required: &["subAcct", "apiKey"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"perm\":{\"type\":\"string\"},\"ip\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"apiKey\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-delete-the-api-key-of-sub-accounts
        "delete_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/delete-apikey",
            post: true,
            public: false,
            keys: &["subAcct", "apiKey"],
            required: &["subAcct", "apiKey"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"apiKey\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out
        "set_sub_account_transfer_out" => RiskEndpoint {
            path: "/api/v5/users/subaccount/set-transfer-out",
            post: true,
            public: false,
            keys: &["subAcct", "canTransOut"],
            required: &["subAcct"],
            bools: &["canTransOut"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"canTransOut\":{\"type\":\"boolean\"}},\"required\":[\"subAcct\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#announcement-get-announcements
        "get_announcements" => RiskEndpoint {
            path: "/api/v5/support/announcements",
            post: false,
            public: true,
            keys: &["annType", "page"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"annType\":{\"type\":\"string\"},\"page\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#announcement-get-announcement-types
        "get_announcement_types" => RiskEndpoint {
            path: "/api/v5/support/announcement-types",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-place-grid-algo-order
        "trading_bot_grid_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/order-algo",
            post: true,
            public: false,
            keys: &[
                "instId",
                "algoOrdType",
                "maxPx",
                "minPx",
                "gridNum",
                "runType",
                "tpTriggerPx",
                "slTriggerPx",
                "algoClOrdId",
                "tag",
                "profitSharingRatio",
                "triggerParams",
                "quoteSz",
                "baseSz",
                "tradeQuoteCcy",
                "sz",
                "direction",
                "lever",
                "basePos",
                "tpRatio",
                "slRatio",
            ],
            required: &["instId", "algoOrdType", "maxPx", "minPx", "gridNum"],
            bools: &["basePos"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"maxPx\":{\"type\":\"string\",\"description\":\"Upper price of price range\"},\"minPx\":{\"type\":\"string\",\"description\":\"Lower price of price range\"},\"gridNum\":{\"type\":\"string\",\"description\":\"Grid quantity\"},\"runType\":{\"type\":\"string\",\"description\":\"Grid type 1 : Arithmetic, 2 : Geometric Default is Arithmetic\"},\"tpTriggerPx\":{\"type\":\"string\",\"description\":\"TP tigger price Applicable to Spot grid / Contract grid\"},\"slTriggerPx\":{\"type\":\"string\",\"description\":\"SL tigger price Applicable to Spot grid / Contract grid\"},\"algoClOrdId\":{\"type\":\"string\",\"description\":\"Client-supplied Algo ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag\"},\"profitSharingRatio\":{\"type\":\"string\",\"description\":\"Profit sharing ratio, it only supports these values 0 , 0.1 , 0.2 , 0.3 0.1 represents 10%\"},\"triggerParams\":{\"type\":\"array\",\"description\":\"Trigger Parameters Applicable to Spot grid / Contract grid\",\"items\":{\"type\":\"object\",\"properties\":{\"triggerAction\":{\"type\":\"string\",\"description\":\"Trigger action start stop\"},\"triggerStrategy\":{\"type\":\"string\",\"description\":\"Trigger strategy instant price rsi Default is instant\"},\"delaySeconds\":{\"type\":\"string\",\"description\":\"Delay seconds after action triggered\"},\"timeframe\":{\"type\":\"string\",\"description\":\"K-line type 3m , 5m , 15m , 30m ( m : minute) 1H , 4H ( H : hour) 1D ( D : day) This field is only valid when triggerStrategy is rsi\"},\"thold\":{\"type\":\"string\",\"description\":\"Threshold The value should be an integer between 1 to 100 This field is only valid when triggerStrategy is rsi\"},\"triggerCond\":{\"type\":\"string\",\"description\":\"Trigger condition cross_up cross_down above below cross This field is only valid when triggerStrategy is rsi\"},\"timePeriod\":{\"type\":\"string\",\"description\":\"Time Period 14 This field is only valid when triggerStrategy is rsi\"},\"triggerPx\":{\"type\":\"string\",\"description\":\"Trigger Price This field is only valid when triggerStrategy is price\"},\"stopType\":{\"type\":\"string\",\"description\":\"Stop type Spot grid 1 : Sell base currency 2 : Keep base currency Contract grid 1 : Market Close All positions 2 : Keep positions This field is only valid when triggerAction is stop\"}},\"required\":[\"triggerAction\",\"triggerStrategy\"]}},\"quoteSz\":{\"type\":\"string\",\"description\":\"Invest amount for quote currency Either quoteSz or baseSz is required\"},\"baseSz\":{\"type\":\"string\",\"description\":\"Invest amount for base currency Either quoteSz or baseSz is required\"},\"tradeQuoteCcy\":{\"type\":\"string\",\"description\":\"The quote currency for trading. Only applicable to SPOT. The default value is the quote currency of instId, e.g. USD for BTC-USD.\"},\"sz\":{\"type\":\"string\",\"description\":\"Used margin based on USDT\"},\"direction\":{\"type\":\"string\",\"description\":\"Contract grid type long , short , neutral\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage\"},\"basePos\":{\"type\":\"boolean\",\"description\":\"Whether or not open a position when the strategy activates Default is false Neutral contract grid should omit the parameter\"},\"tpRatio\":{\"type\":\"string\",\"description\":\"Take profit ratio, 0.1 represents 10%\"},\"slRatio\":{\"type\":\"string\",\"description\":\"Stop loss ratio, 0.1 represents 10%\"}},\"required\":[\"instId\",\"algoOrdType\",\"maxPx\",\"minPx\",\"gridNum\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-amend-grid-algo-order-basic-param
        "trading_bot_grid_amend_algo_basic_param" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/amend-algo-basic-param",
            post: true,
            public: false,
            keys: &["algoId", "minPx", "maxPx", "gridNum", "topupAmount"],
            required: &["algoId", "minPx", "maxPx", "gridNum"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"minPx\":{\"type\":\"string\",\"description\":\"Minimum price range\"},\"maxPx\":{\"type\":\"string\",\"description\":\"Maximum price range\"},\"gridNum\":{\"type\":\"string\",\"description\":\"Grid quantity\"},\"topupAmount\":{\"type\":\"string\",\"description\":\"Contract grid only. Optional client-supplied top up investment amount. If this is not supplied or explicitly supplied as \\\"0\\\", the required top up investment amount to edit grid parameters is topped up by default\"}},\"required\":[\"algoId\",\"minPx\",\"maxPx\",\"gridNum\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-amend-grid-algo-order
        "trading_bot_grid_amend_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/amend-order-algo",
            post: true,
            public: false,
            keys: &[
                "algoId",
                "instId",
                "slTriggerPx",
                "tpTriggerPx",
                "tpRatio",
                "slRatio",
                "topUpAmt",
                "triggerParams",
            ],
            required: &["algoId", "instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"slTriggerPx\":{\"type\":\"string\",\"description\":\"New stop-loss trigger price if slTriggerPx is set \\\"\\\" means stop-loss trigger price is canceled. Either slTriggerPx or tpTriggerPx is required.\",\"x-allow-empty\":true},\"tpTriggerPx\":{\"type\":\"string\",\"description\":\"New take-profit trigger price if tpTriggerPx is set \\\"\\\" means take-profit trigger price is canceled.\",\"x-allow-empty\":true},\"tpRatio\":{\"type\":\"string\",\"description\":\"Take profit ratio, 0.1 represents 10%, only applicable to contract grid if it is set \\\"\\\" means take-profit ratio is canceled.\",\"x-allow-empty\":true},\"slRatio\":{\"type\":\"string\",\"description\":\"Stop loss ratio, 0.1 represents 10%, only applicable to contract grid` if it is set \\\"\\\" means stop-loss ratio is canceled.\",\"x-allow-empty\":true},\"topUpAmt\":{\"type\":\"string\",\"description\":\"Top up amount, only applicable to spot grid\"},\"triggerParams\":{\"type\":\"array\",\"description\":\"Trigger Parameters\",\"items\":{\"type\":\"object\",\"properties\":{\"triggerAction\":{\"type\":\"string\",\"description\":\"Trigger action start stop\"},\"triggerStrategy\":{\"type\":\"string\",\"description\":\"Trigger strategy instant price rsi\"},\"triggerPx\":{\"type\":\"string\",\"description\":\"Trigger Price This field is only valid when triggerStrategy is price\"},\"stopType\":{\"type\":\"string\",\"description\":\"Stop type Spot grid 1 : Sell base currency 2 : Keep base currency Contract grid 1 : Market Close All positions 2 : Keep positions This field is only valid when triggerAction is stop\"}},\"required\":[\"triggerAction\",\"triggerStrategy\"]}}},\"required\":[\"algoId\",\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-stop-grid-algo-order
        "trading_bot_grid_stop_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/stop-order-algo",
            post: true,
            public: false,
            keys: &["orders"],
            required: &["orders"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"orders\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"stopType\":{\"type\":\"string\",\"description\":\"Stop type Spot grid 1 : Sell base currency 2 : Keep base currency Contract grid 1 : Market Close All positions 2 : Keep positions\"}},\"required\":[\"algoId\",\"instId\",\"algoOrdType\",\"stopType\"]},\"minItems\":1,\"maxItems\":10}},\"required\":[\"orders\"],\"x-body-array\":true}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-close-position-for-contract-grid
        "trading_bot_grid_close_position" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/close-position",
            post: true,
            public: false,
            keys: &["algoId", "mktClose", "sz", "px"],
            required: &["algoId", "mktClose"],
            bools: &["mktClose"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"mktClose\":{\"type\":\"boolean\",\"description\":\"Market close all the positions or not true : Market close all position, false : Close part of position\"},\"sz\":{\"type\":\"string\",\"description\":\"Close position amount, with unit of contract If mktClose is false , the parameter is required.\"},\"px\":{\"type\":\"string\",\"description\":\"Close position price If mktClose is false , the parameter is required.\"}},\"required\":[\"algoId\",\"mktClose\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-cancel-close-position-order-for-contract-grid
        "trading_bot_grid_cancel_close_order" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/cancel-close-order",
            post: true,
            public: false,
            keys: &["algoId", "ordId"],
            required: &["algoId", "ordId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"ordId\":{\"type\":\"string\",\"description\":\"Close position order ID\"}},\"required\":[\"algoId\",\"ordId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-instant-trigger-grid-algo-order
        "trading_bot_grid_order_instant_trigger" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/order-instant-trigger",
            post: true,
            public: false,
            keys: &["algoId", "topUpAmt"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"topUpAmt\":{\"type\":\"string\",\"description\":\"Top up amount, only applicable to spot grid\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-list
        "get_trading_bot_grid_orders_algo_pending" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/orders-algo-pending",
            post: false,
            public: false,
            keys: &[
                "algoOrdType",
                "algoId",
                "instId",
                "instType",
                "after",
                "before",
                "limit",
            ],
            required: &["algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT MARGIN FUTURES SWAP\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-history
        "get_trading_bot_grid_orders_algo_history" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/orders-algo-history",
            post: false,
            public: false,
            keys: &[
                "algoOrdType",
                "algoId",
                "instId",
                "instType",
                "after",
                "before",
                "limit",
            ],
            required: &["algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT MARGIN FUTURES SWAP\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-details
        "get_trading_bot_grid_orders_algo_details" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/orders-algo-details",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId"],
            required: &["algoOrdType", "algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoOrdType\",\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-sub-orders
        "get_trading_bot_grid_sub_orders" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/sub-orders",
            post: false,
            public: false,
            keys: &[
                "algoOrdType",
                "algoId",
                "type",
                "groupId",
                "after",
                "before",
                "limit",
            ],
            required: &["algoOrdType", "algoId", "type"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"type\":{\"type\":\"string\",\"description\":\"Sub order state live filled\"},\"groupId\":{\"type\":\"string\",\"description\":\"Group ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested ordId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested ordId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoOrdType\",\"algoId\",\"type\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-positions
        "get_trading_bot_grid_positions" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/positions",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId"],
            required: &["algoOrdType", "algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_grid : Contract grid\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoOrdType\",\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-spot-grid-withdraw-income
        "trading_bot_grid_withdraw_income" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/withdraw-income",
            post: true,
            public: false,
            keys: &["algoId"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-compute-margin-balance
        "trading_bot_grid_compute_margin_balance" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/compute-margin-balance",
            post: true,
            public: false,
            keys: &["algoId", "type", "amt"],
            required: &["algoId", "type"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"type\":{\"type\":\"string\",\"description\":\"Adjust margin balance type add reduce\"},\"amt\":{\"type\":\"string\",\"description\":\"Adjust margin balance amount Default is zero.\"}},\"required\":[\"algoId\",\"type\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-adjust-margin-balance
        "trading_bot_grid_margin_balance" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/margin-balance",
            post: true,
            public: false,
            keys: &["algoId", "type", "amt", "percent"],
            required: &["algoId", "type"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"type\":{\"type\":\"string\",\"description\":\"Adjust margin balance type add reduce\"},\"amt\":{\"type\":\"string\",\"description\":\"Adjust margin balance amount Either amt or percent is required.\"},\"percent\":{\"type\":\"string\",\"description\":\"Adjust margin balance percentage\"}},\"required\":[\"algoId\",\"type\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-add-investment
        "trading_bot_grid_adjust_investment" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/adjust-investment",
            post: true,
            public: false,
            keys: &["algoId", "amt", "allowReinvestProfit"],
            required: &["algoId", "amt"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"amt\":{\"type\":\"string\",\"description\":\"The amount is going to be added\"},\"allowReinvestProfit\":{\"type\":\"string\",\"description\":\"Whether reinvesting profits, only applicable to spot grid. true or false . The default is true.\"}},\"required\":[\"algoId\",\"amt\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-ai-parameter-public
        "get_trading_bot_grid_ai_param" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/ai-param",
            post: false,
            public: true,
            keys: &["algoOrdType", "instId", "direction", "duration"],
            required: &["algoOrdType", "instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"direction\":{\"type\":\"string\",\"description\":\"Contract grid type long , short , neutral Required in the case of contract_grid\"},\"duration\":{\"type\":\"string\",\"description\":\"Back testing duration in number of days Spot grid default is 7D with available durations of 7D , 30D and 180D Contract grid default is 14D with available durations of 7D , 14D and 30D\"}},\"required\":[\"algoOrdType\",\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-compute-min-investment-public
        "trading_bot_grid_min_investment" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/min-investment",
            post: true,
            public: true,
            keys: &[
                "instId",
                "algoOrdType",
                "maxPx",
                "minPx",
                "gridNum",
                "runType",
                "direction",
                "lever",
                "basePos",
                "investmentType",
                "triggerStrategy",
                "topUpAmt",
                "investmentData",
            ],
            required: &[
                "instId",
                "algoOrdType",
                "maxPx",
                "minPx",
                "gridNum",
                "runType",
            ],
            bools: &["basePos"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"maxPx\":{\"type\":\"string\",\"description\":\"Upper price of price range\"},\"minPx\":{\"type\":\"string\",\"description\":\"Lower price of price range\"},\"gridNum\":{\"type\":\"string\",\"description\":\"Grid quantity\"},\"runType\":{\"type\":\"string\",\"description\":\"Grid type 1 : Arithmetic, 2 : Geometric\"},\"direction\":{\"type\":\"string\",\"description\":\"Contract grid type long , short , neutral Only applicable to contract grid\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage Only applicable to contract grid\"},\"basePos\":{\"type\":\"boolean\",\"description\":\"Whether or not open a position when the strategy activates Default is false Neutral contract grid should omit the parameter Only applicable to contract grid\"},\"investmentType\":{\"type\":\"string\",\"description\":\"Investment type, only applicable to grid quote base dual\"},\"triggerStrategy\":{\"type\":\"string\",\"description\":\"Trigger stragety, instant price rsi\"},\"topUpAmt\":{\"type\":\"string\",\"description\":\"Top up amount, only applicable to spot grid\"},\"investmentData\":{\"type\":\"array\",\"description\":\"Invest Data\",\"items\":{\"type\":\"object\",\"properties\":{\"amt\":{\"type\":\"string\",\"description\":\"Invest amount\"},\"ccy\":{\"type\":\"string\",\"description\":\"Invest currency\"}},\"required\":[\"amt\",\"ccy\"]}}},\"required\":[\"instId\",\"algoOrdType\",\"maxPx\",\"minPx\",\"gridNum\",\"runType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-rsi-back-testing-public
        "get_trading_bot_public_rsi_back_testing" => RiskEndpoint {
            path: "/api/v5/tradingBot/public/rsi-back-testing",
            post: false,
            public: true,
            keys: &[
                "instId",
                "timeframe",
                "thold",
                "timePeriod",
                "triggerCond",
                "duration",
            ],
            required: &["instId", "timeframe", "thold", "timePeriod"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT Only applicable to SPOT\"},\"timeframe\":{\"type\":\"string\",\"description\":\"K-line type 3m , 5m , 15m , 30m ( m : minute) 1H , 4H ( H : hour) 1D ( D : day)\"},\"thold\":{\"type\":\"string\",\"description\":\"Threshold The value should be an integer between 1 to 100\"},\"timePeriod\":{\"type\":\"string\",\"description\":\"Time Period 14\"},\"triggerCond\":{\"type\":\"string\",\"description\":\"Trigger condition cross_up cross_down above below cross Default is cross_down\"},\"duration\":{\"type\":\"string\",\"description\":\"Back testing duration 1M ( M : month) Default is 1M\"}},\"required\":[\"instId\",\"timeframe\",\"thold\",\"timePeriod\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-max-grid-quantity-public
        "get_trading_bot_grid_grid_quantity" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/grid-quantity",
            post: false,
            public: true,
            keys: &[
                "instId",
                "runType",
                "algoOrdType",
                "maxPx",
                "minPx",
                "lever",
            ],
            required: &["instId", "runType", "algoOrdType", "maxPx", "minPx"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"runType\":{\"type\":\"string\",\"description\":\"Grid type 1 : Arithmetic 2 : Geometric\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"maxPx\":{\"type\":\"string\",\"description\":\"Upper price of price range\"},\"minPx\":{\"type\":\"string\",\"description\":\"Lower price of price range\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage, it is required for contract grid\"}},\"required\":[\"instId\",\"runType\",\"algoOrdType\",\"maxPx\",\"minPx\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-copy-grid-algo-order
        "trading_bot_grid_copy_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/grid/copy-order-algo",
            post: true,
            public: false,
            keys: &[
                "instId",
                "algoOrdType",
                "sourceAlgoId",
                "quoteSz",
                "lever",
                "autoReserve",
                "sz",
                "actualMarginSz",
                "extraMarginSz",
                "algoClOrdId",
                "tag",
            ],
            required: &["instId", "algoOrdType", "sourceAlgoId"],
            bools: &["autoReserve"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type grid : Spot grid contract_grid : Contract grid\"},\"sourceAlgoId\":{\"type\":\"string\",\"description\":\"Lead algo order ID to follow and copy from\"},\"quoteSz\":{\"type\":\"string\",\"description\":\"Quote currency investment amount Only applicable to grid\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage Only applicable to contract_grid\"},\"autoReserve\":{\"type\":\"boolean\",\"description\":\"Whether to auto-reserve margin. Only applicable to contract_grid true : Actual margin and extra margin are automatically calculated based on sz false : Manually specify actualMarginSz and extraMarginSz\"},\"sz\":{\"type\":\"string\",\"description\":\"Total investment amount in USDT. Required when autoReserve is true Only applicable to contract_grid\"},\"actualMarginSz\":{\"type\":\"string\",\"description\":\"Actual margin. Required when autoReserve is false Only applicable to contract_grid\"},\"extraMarginSz\":{\"type\":\"string\",\"description\":\"Extra margin reserved. Defaults to 0 when unspecified Only applicable to contract_grid\"},\"algoClOrdId\":{\"type\":\"string\",\"description\":\"Client-supplied Algo ID\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag\"}},\"required\":[\"instId\",\"algoOrdType\",\"sourceAlgoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-place-dca-algo-order
        "trading_bot_dca_create" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/create",
            post: true,
            public: false,
            keys: &[
                "instId",
                "algoOrdType",
                "initOrdAmt",
                "allowReinvest",
                "safetyOrdAmt",
                "maxSafetyOrds",
                "pxSteps",
                "pxStepsMult",
                "volMult",
                "tpPct",
                "slPct",
                "slMode",
                "direction",
                "lever",
                "triggerParams",
                "profitSharingRatio",
                "trackingMode",
                "tag",
                "algoClOrdId",
                "tradeQuoteCcy",
            ],
            required: &[
                "instId",
                "algoOrdType",
                "initOrdAmt",
                "maxSafetyOrds",
                "tpPct",
                "lever",
                "triggerParams",
            ],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"initOrdAmt\":{\"type\":\"string\",\"description\":\"Initial order amount\"},\"allowReinvest\":{\"type\":\"string\",\"description\":\"Whether to reinvest profit. Only applicable to Contract DCA true or false , default is true\"},\"safetyOrdAmt\":{\"type\":\"string\",\"description\":\"Safety order amount When maxSafetyOrds >= 1, safetyOrdAmt is required\"},\"maxSafetyOrds\":{\"type\":\"string\",\"description\":\"Max number of safety orders\"},\"pxSteps\":{\"type\":\"string\",\"description\":\"Safety order price step When maxSafetyOrds >= 1, pxSteps is required\"},\"pxStepsMult\":{\"type\":\"string\",\"description\":\"Price step multiplier When maxSafetyOrds >= 1, pxStepsMult is required\"},\"volMult\":{\"type\":\"string\",\"description\":\"Safety order amount multiplier When maxSafetyOrds >= 1, volMult is required\"},\"tpPct\":{\"type\":\"string\",\"description\":\"Take-profit target per cycle 0.05 represents 5%\"},\"slPct\":{\"type\":\"string\",\"description\":\"Stop-loss target 0.05 represents 5%\"},\"slMode\":{\"type\":\"string\",\"description\":\"Stop-loss mode limit : Limit order market : Market order\"},\"direction\":{\"type\":\"string\",\"description\":\"Contract DCA type. Only applicable to contract_dca long : Long position, short : Short position\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage Only applicable to contract_dca\"},\"triggerParams\":{\"type\":\"array\",\"description\":\"Trigger parameters\",\"items\":{\"type\":\"object\",\"properties\":{\"triggerAction\":{\"type\":\"string\",\"description\":\"Trigger action Contract DCA: start : Start bot Spot DCA: start : Start bot\"},\"triggerStrategy\":{\"type\":\"string\",\"description\":\"Trigger strategy Contract DCA: instant : Instant trigger, price : Price trigger, rsi : RSI indicator trigger, default is instant Spot DCA: instant : Instant trigger, rsi : RSI indicator trigger, default is instant\"},\"timeframe\":{\"type\":\"string\",\"description\":\"K-line type 3m , 5m , 15m , 30m (m: minute) 1H , 4H (H: hour) 1D (D: day) This field is only valid when triggerStrategy is rsi\"},\"thold\":{\"type\":\"string\",\"description\":\"Threshold Integer between [1, 100] This field is only valid when triggerStrategy is rsi\"},\"triggerCond\":{\"type\":\"string\",\"description\":\"Trigger condition cross_up : Cross up cross_down : Cross down above : Above below : Below cross : Cross This field is only valid when triggerStrategy is rsi\"},\"timePeriod\":{\"type\":\"string\",\"description\":\"Time period 14 This field is only valid when triggerStrategy is rsi\"},\"triggerPx\":{\"type\":\"string\",\"description\":\"Trigger price This field is only valid when triggerStrategy is price Only applicable to contract_dca\"}},\"required\":[\"triggerAction\",\"triggerStrategy\"]}},\"profitSharingRatio\":{\"type\":\"string\",\"description\":\"Lead trader profit sharing ratio. Only fixed profit sharing is supported. Only applicable to contract_dca 0 , 0.1 , 0.2 , 0.3\"},\"trackingMode\":{\"type\":\"string\",\"description\":\"Tracking mode. Only applicable to contract_dca sync : Synchronous, async : Asynchronous\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag\"},\"algoClOrdId\":{\"type\":\"string\",\"description\":\"Client-supplied Algo ID\"},\"tradeQuoteCcy\":{\"type\":\"string\",\"description\":\"Quote currency for trading. Only applicable to spot_dca\"}},\"required\":[\"instId\",\"algoOrdType\",\"initOrdAmt\",\"maxSafetyOrds\",\"tpPct\",\"lever\",\"triggerParams\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-spot-dca-basic-param
        "trading_bot_dca_amend_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/amend-order-algo",
            post: true,
            public: false,
            keys: &[
                "algoId",
                "pxSteps",
                "pxStepsMult",
                "volMult",
                "tpPct",
                "slPct",
                "initOrdAmt",
                "safetyOrdAmt",
                "maxSafetyOrds",
                "reserveFunds",
                "triggerParams",
            ],
            required: &[
                "algoId",
                "pxSteps",
                "pxStepsMult",
                "volMult",
                "tpPct",
                "slPct",
                "initOrdAmt",
                "safetyOrdAmt",
                "maxSafetyOrds",
                "reserveFunds",
                "triggerParams",
            ],
            bools: &["reserveFunds"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"pxSteps\":{\"type\":\"string\",\"description\":\"Price step ratio (price gap to trigger the first safety order)\"},\"pxStepsMult\":{\"type\":\"string\",\"description\":\"Price step multiplier\"},\"volMult\":{\"type\":\"string\",\"description\":\"Amount multiplier\"},\"tpPct\":{\"type\":\"string\",\"description\":\"Take-profit target, e.g. 0.05 represents 5%\"},\"slPct\":{\"type\":\"string\",\"description\":\"Stop-loss target, e.g. 0.05 represents 5%\"},\"initOrdAmt\":{\"type\":\"string\",\"description\":\"Initial order amount (in quote currency)\"},\"safetyOrdAmt\":{\"type\":\"string\",\"description\":\"Safety order amount (in quote currency)\"},\"maxSafetyOrds\":{\"type\":\"string\",\"description\":\"Maximum number of safety orders\"},\"reserveFunds\":{\"type\":\"boolean\",\"description\":\"Whether to reserve all funds true : reserve funds false : do not reserve funds\"},\"triggerParams\":{\"type\":\"array\",\"description\":\"Signal trigger parameters\",\"items\":{\"type\":\"object\",\"properties\":{\"triggerAction\":{\"type\":\"string\",\"description\":\"Trigger action start : start the DCA bot\"},\"triggerStrategy\":{\"type\":\"string\",\"description\":\"Trigger strategy instant : trigger immediately rsi : RSI indicator trigger\"},\"timeframe\":{\"type\":\"string\",\"description\":\"Candlestick type 3m , 5m , 15m , 30m ( m = minutes) 1H , 4H ( H = hours) 1D ( D = days) Only valid when triggerStrategy is rsi\"},\"thold\":{\"type\":\"string\",\"description\":\"Threshold, integer in range [1, 100] Only valid when triggerStrategy is rsi\"},\"triggerCond\":{\"type\":\"string\",\"description\":\"Trigger condition cross_up : cross upward cross_down : cross downward above : above below : below cross : cross Only valid when triggerStrategy is rsi\"},\"timePeriod\":{\"type\":\"string\",\"description\":\"Period, e.g. 14 Only valid when triggerStrategy is rsi\"}},\"required\":[]}}},\"required\":[\"algoId\",\"pxSteps\",\"pxStepsMult\",\"volMult\",\"tpPct\",\"slPct\",\"initOrdAmt\",\"safetyOrdAmt\",\"maxSafetyOrds\",\"reserveFunds\",\"triggerParams\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-stop-dca-algo-order
        "trading_bot_dca_stop" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/stop",
            post: true,
            public: false,
            keys: &["algoId", "algoOrdType", "stopType"],
            required: &["algoId", "algoOrdType", "stopType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"stopType\":{\"type\":\"string\",\"description\":\"Stop type contract_dca : 1 : Market close all positions, 2 : Keep positions spot_dca : 1 : Sell base currency, 2 : Keep base currency\"}},\"required\":[\"algoId\",\"algoOrdType\",\"stopType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-details
        "get_trading_bot_dca_ongoing_list" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/ongoing-list",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId", "after", "before", "limit"],
            required: &["algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-history
        "get_trading_bot_dca_history_list" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/history-list",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId", "after", "before", "limit"],
            required: &["algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-sub-orders
        "get_trading_bot_dca_orders" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/orders",
            post: false,
            public: false,
            keys: &[
                "algoId",
                "algoOrdType",
                "cycleId",
                "after",
                "before",
                "limit",
            ],
            required: &["algoId", "algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"cycleId\":{\"type\":\"string\",\"description\":\"Cycle ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested ordId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested ordId\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoId\",\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-add-investment
        "trading_bot_dca_orders_manual_buy" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/orders/manual-buy",
            post: true,
            public: false,
            keys: &[
                "algoId",
                "algoOrdType",
                "price",
                "amt",
                "ordType",
                "tradeQuoteCcy",
            ],
            required: &["algoId", "algoOrdType", "price", "amt"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"price\":{\"type\":\"string\",\"description\":\"Manual added order limit price\"},\"amt\":{\"type\":\"string\",\"description\":\"Amount\"},\"ordType\":{\"type\":\"string\",\"description\":\"Order type limit : Limit order market : Market order Only applicable to spot_dca\"},\"tradeQuoteCcy\":{\"type\":\"string\",\"description\":\"Quote currency for trading Only applicable to spot_dca\"}},\"required\":[\"algoId\",\"algoOrdType\",\"price\",\"amt\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-dca-reinvestment
        "trading_bot_dca_settings_reinvestment" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/settings/reinvestment",
            post: true,
            public: false,
            keys: &["algoId", "algoOrdType", "allowReinvest"],
            required: &["algoId", "algoOrdType", "allowReinvest"],
            bools: &["allowReinvest"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order\"},\"allowReinvest\":{\"type\":\"boolean\",\"description\":\"Whether to reinvest profit true or false\"}},\"required\":[\"algoId\",\"algoOrdType\",\"allowReinvest\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-dca-take-profit-settings
        "trading_bot_dca_settings_take_profit" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/settings/take-profit",
            post: true,
            public: false,
            keys: &["algoId", "algoOrdType", "tpPrice"],
            required: &["algoId", "algoOrdType", "tpPrice"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order\"},\"tpPrice\":{\"type\":\"string\",\"description\":\"Take-profit price\"}},\"required\":[\"algoId\",\"algoOrdType\",\"tpPrice\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-position-details
        "get_trading_bot_dca_position_details" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/position-details",
            post: false,
            public: false,
            keys: &["algoId", "algoOrdType"],
            required: &["algoId", "algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"}},\"required\":[\"algoId\",\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-cycle-list
        "get_trading_bot_dca_cycle_list" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/cycle-list",
            post: false,
            public: false,
            keys: &[
                "algoId",
                "algoOrdType",
                "instId",
                "after",
                "before",
                "limit",
            ],
            required: &["algoId", "algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract_dca : Contract DCA order spot_dca : Spot DCA order\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested cycleId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested cycleId\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoId\",\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-add-dca-margin
        "trading_bot_dca_margin_add" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/margin/add",
            post: true,
            public: false,
            keys: &["algoId", "amt"],
            required: &["algoId", "amt"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"amt\":{\"type\":\"string\",\"description\":\"Margin add amount\"}},\"required\":[\"algoId\",\"amt\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-reduce-dca-margin
        "trading_bot_dca_margin_reduce" => RiskEndpoint {
            path: "/api/v5/tradingBot/dca/margin/reduce",
            post: true,
            public: false,
            keys: &["algoId", "amt"],
            required: &["algoId", "amt"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"amt\":{\"type\":\"string\",\"description\":\"Margin reduction amount\"}},\"required\":[\"algoId\",\"amt\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-create-signal
        "trading_bot_signal_create_signal" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/create-signal",
            post: true,
            public: false,
            keys: &["signalChanName", "signalChanDesc"],
            required: &["signalChanName"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"signalChanName\":{\"type\":\"string\",\"description\":\"Signal channel name\"},\"signalChanDesc\":{\"type\":\"string\",\"description\":\"Signal channel description\"}},\"required\":[\"signalChanName\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signals
        "get_trading_bot_signal_signals" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/signals",
            post: false,
            public: false,
            keys: &[
                "signalSourceType",
                "signalChanId",
                "after",
                "before",
                "limit",
            ],
            required: &["signalSourceType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"signalSourceType\":{\"type\":\"string\",\"description\":\"Signal source type 1 : Created by yourself 2 : Subscribe 3 : Free signal\"},\"signalChanId\":{\"type\":\"string\",\"description\":\"Signal channel id\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records signalChanId earlier than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records signalChanId newer than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"signalSourceType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-create-signal-bot
        "trading_bot_signal_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/order-algo",
            post: true,
            public: false,
            keys: &[
                "signalChanId",
                "lever",
                "investAmt",
                "subOrdType",
                "includeAll",
                "instIds",
                "ratio",
                "entrySettingParam",
                "exitSettingParam",
            ],
            required: &["signalChanId", "lever", "investAmt", "subOrdType"],
            bools: &["includeAll"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"signalChanId\":{\"type\":\"string\",\"description\":\"Signal channel Id\"},\"lever\":{\"type\":\"string\",\"description\":\"Leverage Only applicable to contract signal\"},\"investAmt\":{\"type\":\"string\",\"description\":\"Investment amount\"},\"subOrdType\":{\"type\":\"string\",\"description\":\"Sub order type 1 \\uff1alimit order 2 \\uff1amarket order 9 \\uff1atradingView signal\"},\"includeAll\":{\"type\":\"boolean\",\"description\":\"Whether to include all USDT-margined contract.The default value is false . true : include false : exclude\"},\"instIds\":{\"type\":\"string\",\"description\":\"Instrument IDs. Single currency or multiple currencies separated with comma. When includeAll is true , it is ignored\"},\"ratio\":{\"type\":\"string\",\"description\":\"Price offset ratio, calculate the limit price as a percentage offset from the best bid/ask price. Only applicable to subOrdType is limit order\"},\"entrySettingParam\":{\"type\":\"object\",\"description\":\"Entry setting\",\"properties\":{\"allowMultipleEntry\":{\"type\":\"boolean\",\"description\":\"Whether or not allow multiple entries in the same direction for the same trading pairs.The default value is true \\u3002 true \\uff1aAllow false \\uff1aProhibit\"},\"entryType\":{\"type\":\"string\",\"description\":\"Entry type 1 : TradingView signal 2 : Fixed margin 3 : Contracts 4 : Percentage of free margin 5 : Percentage of the initial invested margin\"},\"amt\":{\"type\":\"string\",\"description\":\"Amount per order Only applicable to entryType in 2 / 3\"},\"ratio\":{\"type\":\"string\",\"description\":\"Amount ratio per order Only applicable to entryType in 4 / 5\"}},\"required\":[]},\"exitSettingParam\":{\"type\":\"object\",\"description\":\"Exit setting\",\"properties\":{\"tpSlType\":{\"type\":\"string\",\"description\":\"Type of set the take-profit and stop-loss trigger price pnl : Based on the estimated profit and loss percentage from the entry point price : Based on price increase or decrease from the crypto\\u2019s entry price\"},\"tpPct\":{\"type\":\"string\",\"description\":\"Take-profit percentage\"},\"slPct\":{\"type\":\"string\",\"description\":\"Stop-loss percentage\"}},\"required\":[]}},\"required\":[\"signalChanId\",\"lever\",\"investAmt\",\"subOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-cancel-signal-bots
        "trading_bot_signal_stop_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/stop-order-algo",
            post: true,
            public: false,
            keys: &["orders"],
            required: &["orders"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"orders\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoId\"]},\"minItems\":1,\"maxItems\":10}},\"required\":[\"orders\"],\"x-body-array\":true}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-adjust-margin-balance
        "trading_bot_signal_margin_balance" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/margin-balance",
            post: true,
            public: false,
            keys: &["algoId", "type", "amt", "allowReinvest"],
            required: &["algoId", "type", "amt"],
            bools: &["allowReinvest"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"type\":{\"type\":\"string\",\"description\":\"Adjust margin balance type add reduce\"},\"amt\":{\"type\":\"string\",\"description\":\"Adjust margin balance amount Either amt or percent is required.\"},\"allowReinvest\":{\"type\":\"boolean\",\"description\":\"Whether to reinvest with newly added margin. The default value is false . false :it will be used as passive margin to prevent liquidation and will not be used as active investment true :the margin added here will furthermore be accounted for in calculations of your total investment amount, and furthermore your order size\\u3002 Only applicable to your signal comes in with an \\u201cinvestmentType\\u201d of \\u201cpercentage_investment\\u201d\"}},\"required\":[\"algoId\",\"type\",\"amt\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-amend-tpsl
        "trading_bot_signal_amend_tpsl" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/amendTPSL",
            post: true,
            public: false,
            keys: &["algoId", "exitSettingParam"],
            required: &["algoId", "exitSettingParam"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"exitSettingParam\":{\"type\":\"object\",\"description\":\"Exit setting\",\"properties\":{\"tpSlType\":{\"type\":\"string\",\"description\":\"Type of set the take-profit and stop-loss trigger price pnl : Based on the estimated profit and loss percentage from the entry point price : Based on price increase or decrease from the crypto\\u2019s entry price\"},\"tpPct\":{\"type\":\"string\",\"description\":\"Take-profit percentage\"},\"slPct\":{\"type\":\"string\",\"description\":\"Stop-loss percentage\"}},\"required\":[\"tpSlType\"]}},\"required\":[\"algoId\",\"exitSettingParam\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-set-instruments
        "trading_bot_signal_set_instruments" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/set-instruments",
            post: true,
            public: false,
            keys: &["algoId", "instIds", "includeAll"],
            required: &["algoId", "instIds", "includeAll"],
            bools: &["includeAll"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instIds\":{\"type\":\"array\",\"description\":\"Instrument IDs. When includeAll is true , it is ignored\",\"items\":{\"type\":\"string\"}},\"includeAll\":{\"type\":\"boolean\",\"description\":\"Whether to include all USDT-margined contract.The default value is false . true : include false : exclude\"}},\"required\":[\"algoId\",\"instIds\",\"includeAll\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-order-details
        "get_trading_bot_signal_orders_algo_details" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/orders-algo-details",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId"],
            required: &["algoOrdType", "algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract : Contract signal\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoOrdType\",\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-active-signal-bot
        "get_trading_bot_signal_orders_algo_pending" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/orders-algo-pending",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId", "after", "before", "limit"],
            required: &["algoOrdType", "after"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract : Contract signal\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records algoId earlier than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records algoId newer than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"algoOrdType\",\"after\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-history
        "get_trading_bot_signal_orders_algo_history" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/orders-algo-history",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId", "after", "before", "limit"],
            required: &["algoOrdType", "algoId", "after"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract : Contract signal\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records algoId earlier than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records algoId newer than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"algoOrdType\",\"algoId\",\"after\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-order-positions
        "get_trading_bot_signal_positions" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/positions",
            post: false,
            public: false,
            keys: &["algoOrdType", "algoId"],
            required: &["algoOrdType", "algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract : Contract signal\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoOrdType\",\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-position-history
        "get_trading_bot_signal_positions_history" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/positions-history",
            post: false,
            public: false,
            keys: &["algoId", "instId", "after", "before", "limit"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g.\\uff1a BTC-USD-SWAP\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested uTime , Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested uTime , Unix timestamp format in milliseconds, e.g 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-close-position
        "trading_bot_signal_close_position" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/close-position",
            post: true,
            public: false,
            keys: &["algoId", "instId"],
            required: &["algoId", "instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID\"}},\"required\":[\"algoId\",\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-place-sub-order
        "trading_bot_signal_sub_order" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/sub-order",
            post: true,
            public: false,
            keys: &[
                "instId",
                "algoId",
                "side",
                "ordType",
                "sz",
                "px",
                "reduceOnly",
            ],
            required: &["instId", "algoId", "side", "ordType", "sz"],
            bools: &["reduceOnly"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"side\":{\"type\":\"string\",\"description\":\"Order side, buy sell\"},\"ordType\":{\"type\":\"string\",\"description\":\"Order type market : Market order limit : Limit order\"},\"sz\":{\"type\":\"string\",\"description\":\"Quantity to buy or sell\"},\"px\":{\"type\":\"string\",\"description\":\"Order price. Only applicable to limit order.\"},\"reduceOnly\":{\"type\":\"boolean\",\"description\":\"Whether orders can only reduce in position size. Valid options: true or false . The default value is false . Only applicable to Futures mode / Multi-currency margin\"}},\"required\":[\"instId\",\"algoId\",\"side\",\"ordType\",\"sz\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-cancel-sub-order
        "trading_bot_signal_cancel_sub_order" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/cancel-sub-order",
            post: true,
            public: false,
            keys: &["algoId", "instId", "signalOrdId"],
            required: &["algoId", "instId", "signalOrdId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"signalOrdId\":{\"type\":\"string\",\"description\":\"Order ID\"}},\"required\":[\"algoId\",\"instId\",\"signalOrdId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-sub-orders
        "get_trading_bot_signal_sub_orders" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/sub-orders",
            post: false,
            public: false,
            keys: &[
                "algoId",
                "algoOrdType",
                "state",
                "signalOrdId",
                "after",
                "before",
                "begin",
                "end",
                "limit",
                "type",
                "clOrdId",
            ],
            required: &["algoId", "algoOrdType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"algoOrdType\":{\"type\":\"string\",\"description\":\"Algo order type contract : Contract signal\"},\"state\":{\"type\":\"string\",\"description\":\"Sub order state live partially_filled filled cancelled Either state or signalOrdId is required, if both are passed in, only state is valid.\"},\"signalOrdId\":{\"type\":\"string\",\"description\":\"Sub order ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested ordId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested ordId .\"},\"begin\":{\"type\":\"string\",\"description\":\"Return records of ctime after than the requested timestamp (include), Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"end\":{\"type\":\"string\",\"description\":\"Return records of ctime before than the requested timestamp (include), Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"},\"type\":{\"type\":\"string\",\"description\":\"Sub order type live filled Either type or clOrdId is required, if both are passed in, only clOrdId is valid.\"},\"clOrdId\":{\"type\":\"string\",\"description\":\"Sub order client-supplied ID. It will be deprecated soon\"}},\"required\":[\"algoId\",\"algoOrdType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-event-history
        "get_trading_bot_signal_event_history" => RiskEndpoint {
            path: "/api/v5/tradingBot/signal/event-history",
            post: false,
            public: false,
            keys: &["algoId", "after", "before", "limit"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records eventCtime earlier than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records eventCtime newer than the requested timestamp, Unix timestamp format in milliseconds, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-place-recurring-buy-order
        "trading_bot_recurring_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/order-algo",
            post: true,
            public: false,
            keys: &[
                "stgyName",
                "recurringList",
                "period",
                "recurringDay",
                "recurringHour",
                "recurringTime",
                "timeZone",
                "amt",
                "investmentCcy",
                "tdMode",
                "algoClOrdId",
                "tag",
                "tradeQuoteCcy",
                "source",
                "recurringTimeType",
            ],
            required: &[
                "stgyName",
                "recurringList",
                "period",
                "recurringTime",
                "timeZone",
                "amt",
                "investmentCcy",
                "tdMode",
            ],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"stgyName\":{\"type\":\"string\",\"description\":\"Custom name for trading bot, no more than 40 characters\"},\"recurringList\":{\"type\":\"array\",\"description\":\"Recurring buy info\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Recurring currency, e.g. BTC\"},\"ratio\":{\"type\":\"string\",\"description\":\"Proportion of recurring currency assets, e.g. \\\"0.2\\\" representing 20%\"},\"minPx\":{\"type\":\"string\",\"description\":\"Minimum price of recurring currency. \\\"\\\" means no limit\",\"x-allow-empty\":true},\"maxPx\":{\"type\":\"string\",\"description\":\"Maximum price of recurring currency. \\\"\\\" means no limit\",\"x-allow-empty\":true}},\"required\":[\"ccy\",\"ratio\"]}},\"period\":{\"type\":\"string\",\"description\":\"Period monthly weekly daily hourly\"},\"recurringDay\":{\"type\":\"string\",\"description\":\"Recurring buy date When the period is monthly , the value range is an integer of [1,28] When the period is weekly , the value range is an integer of [1,7] When the period is daily / hourly , the parameter is not required.\"},\"recurringHour\":{\"type\":\"string\",\"description\":\"Recurring buy by hourly 1 / 4 / 8 / 12 , e.g. 4 represents \\\"recurring buy every 4 hour\\\" When the period is hourly , the parameter is required.\"},\"recurringTime\":{\"type\":\"string\",\"description\":\"Recurring buy time, the value range is an integer of [0,23] When the period is hourly , the parameter is the time of the first investment occurs.\"},\"timeZone\":{\"type\":\"string\",\"description\":\"UTC time zone, the value range is an integer of [-12,14] e.g. \\\"8\\\" representing UTC+8 (East 8 District), Beijing Time\"},\"amt\":{\"type\":\"string\",\"description\":\"Quantity invested per cycle\"},\"investmentCcy\":{\"type\":\"string\",\"description\":\"The invested quantity unit, can only be USDT / USDC\"},\"tdMode\":{\"type\":\"string\",\"description\":\"Trading mode Margin mode: cross Non-Margin mode: cash\"},\"algoClOrdId\":{\"type\":\"string\",\"description\":\"Client-supplied Algo ID There will be a value when algo order attaching algoClOrdId is triggered, or it will be \\\"\\\". A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.\",\"x-allow-empty\":true},\"tag\":{\"type\":\"string\",\"description\":\"Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters.\"},\"tradeQuoteCcy\":{\"type\":\"string\",\"description\":\"The quote currency for trading.\"},\"source\":{\"type\":\"array\",\"description\":\"Funding source 1 : Trading account 2 : Funding account 3 : Simple earn account Default is 1\",\"items\":{\"type\":\"string\"}},\"recurringTimeType\":{\"type\":\"string\",\"description\":\"Recurring buy time type 1 : Custom time 2 : Immediate trigger Default is 1\"}},\"required\":[\"stgyName\",\"recurringList\",\"period\",\"recurringTime\",\"timeZone\",\"amt\",\"investmentCcy\",\"tdMode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-order
        "trading_bot_recurring_amend_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/amend-order-algo",
            post: true,
            public: false,
            keys: &["algoId", "stgyName"],
            required: &["algoId", "stgyName"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"stgyName\":{\"type\":\"string\",\"description\":\"New custom name for trading bot after adjustment, no more than 40 characters\"}},\"required\":[\"algoId\",\"stgyName\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-stop-recurring-buy-order
        "trading_bot_recurring_stop_order_algo" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/stop-order-algo",
            post: true,
            public: false,
            keys: &["orders"],
            required: &["orders"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"orders\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoId\"]},\"minItems\":1,\"maxItems\":10}},\"required\":[\"orders\"],\"x-body-array\":true}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-list
        "get_trading_bot_recurring_orders_algo_pending" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/orders-algo-pending",
            post: false,
            public: false,
            keys: &["algoId", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-history
        "get_trading_bot_recurring_orders_algo_history" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/orders-algo-history",
            post: false,
            public: false,
            keys: &["algoId", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-details
        "get_trading_bot_recurring_orders_algo_details" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/orders-algo-details",
            post: false,
            public: false,
            keys: &["algoId"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-sub-orders
        "get_trading_bot_recurring_sub_orders" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/sub-orders",
            post: false,
            public: false,
            keys: &["algoId", "ordId", "after", "before", "limit"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"ordId\":{\"type\":\"string\",\"description\":\"Sub order ID\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested algoId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested algoId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-time
        "trading_bot_recurring_amend_recurring_time" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/amend-recurring-time",
            post: true,
            public: false,
            keys: &[
                "algoId",
                "recurringTimeType",
                "timeZone",
                "period",
                "recurringHour",
                "recurringDay",
                "recurringTime",
            ],
            required: &["algoId", "recurringTimeType", "timeZone", "period"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo ID\"},\"recurringTimeType\":{\"type\":\"string\",\"description\":\"Recurring buy time type 1 : Custom time 2 : Immediate trigger\"},\"timeZone\":{\"type\":\"string\",\"description\":\"UTC time zone, the value range is an integer of [-12,14] e.g. 8 representing UTC+8 (East 8 District), Beijing Time\"},\"period\":{\"type\":\"string\",\"description\":\"Period monthly weekly daily hourly\"},\"recurringHour\":{\"type\":\"string\",\"description\":\"Recurring buy by hourly 1 / 4 / 8 / 12 , e.g. 1 represents \\\"recurring buy every 1 hour\\\" Required when period is hourly\"},\"recurringDay\":{\"type\":\"string\",\"description\":\"Recurring buy date When the period is monthly , the value range is an integer of [1,28] When the period is weekly , the value range is an integer of [1,7] When the period is daily / hourly , the parameter is not required Only required when recurringTimeType is 1\"},\"recurringTime\":{\"type\":\"string\",\"description\":\"Recurring buy time, the value range is an integer of [0,23] Only required when recurringTimeType is 1\"}},\"required\":[\"algoId\",\"recurringTimeType\",\"timeZone\",\"period\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-amount
        "trading_bot_recurring_amend_recurring_amount" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/amend-recurring-amount",
            post: true,
            public: false,
            keys: &["algoId", "amount"],
            required: &["algoId", "amount"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"amount\":{\"type\":\"string\",\"description\":\"Amended recurring buy amount. Only the investment currency used when the strategy was created is supported\"}},\"required\":[\"algoId\",\"amount\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-add-investment
        "trading_bot_recurring_add_investment" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/add-investment",
            post: true,
            public: false,
            keys: &["algoId", "amount"],
            required: &["algoId", "amount"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"amount\":{\"type\":\"string\",\"description\":\"Additional investment amount. Only the investment currency used when the strategy was created is supported\"}},\"required\":[\"algoId\",\"amount\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-pause-recurring-buy
        "trading_bot_recurring_pause" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/pause",
            post: true,
            public: false,
            keys: &["algoId"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-restart-recurring-buy
        "trading_bot_recurring_restart" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/restart",
            post: true,
            public: false,
            keys: &["algoId"],
            required: &["algoId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"}},\"required\":[\"algoId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-price-range
        "trading_bot_recurring_amend_price_range" => RiskEndpoint {
            path: "/api/v5/tradingBot/recurring/amend-price-range",
            post: true,
            public: false,
            keys: &["algoId", "recurringList"],
            required: &["algoId", "recurringList"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"algoId\":{\"type\":\"string\",\"description\":\"Algo order ID\"},\"recurringList\":{\"type\":\"array\",\"description\":\"Price range settings. The currency must be within the scope of the recurring buy currencies\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Recurring buy currency\"},\"minPx\":{\"type\":\"string\",\"description\":\"Minimum price of price range. \\\"\\\" means no limit\",\"x-allow-empty\":true},\"maxPx\":{\"type\":\"string\",\"description\":\"Maximum price of price range. \\\"\\\" means no limit\",\"x-allow-empty\":true}},\"required\":[\"ccy\",\"minPx\",\"maxPx\"]}}},\"required\":[\"algoId\",\"recurringList\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-existing-lead-positions
        "get_copytrading_current_subpositions" => RiskEndpoint {
            path: "/api/v5/copytrading/current-subpositions",
            post: false,
            public: false,
            keys: &["instType", "instId", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP It returns all types by default.\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested subPosId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested subPosId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 500. Default is 500.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-position-history
        "get_copytrading_subpositions_history" => RiskEndpoint {
            path: "/api/v5/copytrading/subpositions-history",
            post: false,
            public: false,
            keys: &["instType", "instId", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP It returns all types by default.\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested subPosId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested subPosId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-place-lead-stop-order
        "copytrading_algo_order" => RiskEndpoint {
            path: "/api/v5/copytrading/algo-order",
            post: true,
            public: false,
            keys: &[
                "instType",
                "subPosId",
                "tpTriggerPx",
                "slTriggerPx",
                "tpOrdPx",
                "slOrdPx",
                "tpTriggerPxType",
                "slTriggerPxType",
                "tag",
            ],
            required: &["subPosId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP , the default value\"},\"subPosId\":{\"type\":\"string\",\"description\":\"Lead position ID\"},\"tpTriggerPx\":{\"type\":\"string\",\"description\":\"Take-profit trigger price. Take-profit order price will be the market price after triggering. At least one of tpTriggerPx and slTriggerPx must be filled The take profit order will be deleted if it is 0\"},\"slTriggerPx\":{\"type\":\"string\",\"description\":\"Stop-loss trigger price. Stop-loss order price will be the market price after triggering. The stop loss order will be deleted if it is 0\"},\"tpOrdPx\":{\"type\":\"string\",\"description\":\"Take-profit order price If the price is -1, take-profit will be executed at the market price, the default is -1 Only applicable to SPOT lead trader\"},\"slOrdPx\":{\"type\":\"string\",\"description\":\"Stop-loss order price If the price is -1, stop-loss will be executed at the market price, the default is -1 Only applicable to SPOT lead trader\"},\"tpTriggerPxType\":{\"type\":\"string\",\"description\":\"Take-profit trigger price type last : last price index : index price mark : mark price Default is last\"},\"slTriggerPxType\":{\"type\":\"string\",\"description\":\"Stop-loss trigger price type last : last price index : index price mark : mark price Default is last\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters.\"}},\"required\":[\"subPosId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-close-lead-position
        "copytrading_close_subposition" => RiskEndpoint {
            path: "/api/v5/copytrading/close-subposition",
            post: true,
            public: false,
            keys: &["instType", "subPosId", "ordType", "px", "tag"],
            required: &["subPosId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP , the default value\"},\"subPosId\":{\"type\":\"string\",\"description\":\"Lead position ID\"},\"ordType\":{\"type\":\"string\",\"description\":\"Order type market \\uff1aMarket order, the default value limit \\uff1aLimit order\"},\"px\":{\"type\":\"string\",\"description\":\"Order price. Only applicable to limit order and SPOT lead trader If the price is 0, the pending order will be canceled. It is modifying order if you set px after placing limit order.\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters.\"}},\"required\":[\"subPosId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-leading-instruments
        "get_copytrading_instruments" => RiskEndpoint {
            path: "/api/v5/copytrading/instruments",
            post: false,
            public: false,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP , the default value\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-leading-instruments
        "copytrading_set_instruments" => RiskEndpoint {
            path: "/api/v5/copytrading/set-instruments",
            post: true,
            public: false,
            keys: &["instType", "instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP , the default value\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-USDT-SWAP. If there are multiple instruments, separate them with commas.\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-profit-sharing-details
        "get_copytrading_profit_sharing_details" => RiskEndpoint {
            path: "/api/v5/copytrading/profit-sharing-details",
            post: false,
            public: false,
            keys: &["instType", "after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP It returns all types by default.\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested profitSharingId\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested profitSharingId\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-total-profit-sharing
        "get_copytrading_total_profit_sharing" => RiskEndpoint {
            path: "/api/v5/copytrading/total-profit-sharing",
            post: false,
            public: false,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP It returns all types by default.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-unrealized-profit-sharing-details
        "get_copytrading_unrealized_profit_sharing_details" => RiskEndpoint {
            path: "/api/v5/copytrading/unrealized-profit-sharing-details",
            post: false,
            public: false,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SPOT SWAP It returns all types by default.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-total-unrealized-profit-sharing
        "get_copytrading_total_unrealized_profit_sharing" => RiskEndpoint {
            path: "/api/v5/copytrading/total-unrealized-profit-sharing",
            post: false,
            public: false,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-profit-sharing-ratio
        "copytrading_amend_profit_sharing_ratio" => RiskEndpoint {
            path: "/api/v5/copytrading/amend-profit-sharing-ratio",
            post: true,
            public: false,
            keys: &["instType", "profitSharingRatio"],
            required: &["profitSharingRatio"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP\"},\"profitSharingRatio\":{\"type\":\"string\",\"description\":\"Profit sharing ratio. 0.1 represents 10%\"}},\"required\":[\"profitSharingRatio\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-account-configuration
        "get_copytrading_config" => RiskEndpoint {
            path: "/api/v5/copytrading/config",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-first-copy-settings
        "copytrading_first_copy_settings" => RiskEndpoint {
            path: "/api/v5/copytrading/first-copy-settings",
            post: true,
            public: false,
            keys: &[
                "instType",
                "uniqueCode",
                "copyMgnMode",
                "copyInstIdType",
                "instId",
                "copyMode",
                "copyTotalAmt",
                "copyAmt",
                "copyRatio",
                "tpRatio",
                "slRatio",
                "slTotalAmt",
                "subPosCloseType",
                "tag",
            ],
            required: &[
                "uniqueCode",
                "copyMgnMode",
                "copyInstIdType",
                "copyTotalAmt",
                "subPosCloseType",
            ],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"copyMgnMode\":{\"type\":\"string\",\"description\":\"Copy margin mode cross : cross isolated : isolated copy : Use the same margin mode as lead trader when opening positions\"},\"copyInstIdType\":{\"type\":\"string\",\"description\":\"Copy contract type setted custom : custom by instId which is required\\uff1b copy : Keep your contracts consistent with this trader by automatically adding or removing contracts when they do\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID. If there are multiple instruments, separate them with commas.\"},\"copyMode\":{\"type\":\"string\",\"description\":\"Copy mode fixed_amount : set the same fixed amount for each order, and copyAmt is required\\uff1b ratio_copy : set amount as a multiple of the lead trader\\u2019s order value, and copyRatio is required The default is fixed_amount\"},\"copyTotalAmt\":{\"type\":\"string\",\"description\":\"Maximum total amount in USDT. The maximum total amount you'll invest at any given time across all orders in this copy trade You won\\u2019t copy new orders if you exceed this amount\"},\"copyAmt\":{\"type\":\"string\",\"description\":\"Copy amount per order in USDT.\"},\"copyRatio\":{\"type\":\"string\",\"description\":\"Copy ratio per order.\"},\"tpRatio\":{\"type\":\"string\",\"description\":\"Take profit per order. 0.1 represents 10%\"},\"slRatio\":{\"type\":\"string\",\"description\":\"Stop loss per order. 0.1 represents 10%\"},\"slTotalAmt\":{\"type\":\"string\",\"description\":\"Total stop loss in USDT for trader. If your net loss (total profit - total loss) reaches this amount, you'll stop copying this trader\"},\"subPosCloseType\":{\"type\":\"string\",\"description\":\"Action type for open positions market_close : immediately close at market price copy_close \\uff1aclose when trader closes manual_close : close manually The default is copy_close\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters.\"}},\"required\":[\"uniqueCode\",\"copyMgnMode\",\"copyInstIdType\",\"copyTotalAmt\",\"subPosCloseType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-copy-settings
        "copytrading_amend_copy_settings" => RiskEndpoint {
            path: "/api/v5/copytrading/amend-copy-settings",
            post: true,
            public: false,
            keys: &[
                "instType",
                "uniqueCode",
                "copyMgnMode",
                "copyInstIdType",
                "instId",
                "copyMode",
                "copyTotalAmt",
                "copyAmt",
                "copyRatio",
                "tpRatio",
                "slRatio",
                "slTotalAmt",
                "subPosCloseType",
                "tag",
            ],
            required: &[
                "uniqueCode",
                "copyMgnMode",
                "copyInstIdType",
                "copyTotalAmt",
                "subPosCloseType",
            ],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"copyMgnMode\":{\"type\":\"string\",\"description\":\"Copy margin mode cross : cross isolated : isolated copy : Use the same margin mode as lead trader when opening positions\"},\"copyInstIdType\":{\"type\":\"string\",\"description\":\"Copy contract type setted custom : custom by instId which is required\\uff1b copy : Keep your contracts consistent with this trader by automatically adding or removing contracts when they do\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID. If there are multiple instruments, separate them with commas.\"},\"copyMode\":{\"type\":\"string\",\"description\":\"Copy mode fixed_amount : set the same fixed amount for each order, and copyAmt is required\\uff1b ratio_copy : set amount as a multiple of the lead trader\\u2019s order value, and copyRatio is required The default is fixed_amount\"},\"copyTotalAmt\":{\"type\":\"string\",\"description\":\"Maximum total amount in USDT. The maximum total amount you'll invest at any given time across all orders in this copy trade You won\\u2019t copy new orders if you exceed this amount\"},\"copyAmt\":{\"type\":\"string\",\"description\":\"Copy amount per order in USDT\"},\"copyRatio\":{\"type\":\"string\",\"description\":\"Copy ratio per order.\"},\"tpRatio\":{\"type\":\"string\",\"description\":\"Take profit per order. 0.1 represents 10%\"},\"slRatio\":{\"type\":\"string\",\"description\":\"Stop loss per order. 0.1 represents 10%\"},\"slTotalAmt\":{\"type\":\"string\",\"description\":\"Total stop loss in USDT for trader. If your net loss (total profit - total loss) reaches this amount, you'll stop copying this trader\"},\"subPosCloseType\":{\"type\":\"string\",\"description\":\"Action type for open positions market_close : immediately close at market price copy_close \\uff1aclose when trader closes manual_close : close manually The default is copy_close\"},\"tag\":{\"type\":\"string\",\"description\":\"Order tag A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 16 characters.\"}},\"required\":[\"uniqueCode\",\"copyMgnMode\",\"copyInstIdType\",\"copyTotalAmt\",\"subPosCloseType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-stop-copying
        "copytrading_stop_copy_trading" => RiskEndpoint {
            path: "/api/v5/copytrading/stop-copy-trading",
            post: true,
            public: false,
            keys: &["instType", "uniqueCode", "subPosCloseType"],
            required: &["uniqueCode", "subPosCloseType"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"subPosCloseType\":{\"type\":\"string\",\"description\":\"Action type for open positions, it is required if you have related copy position market_close : immediately close at market price copy_close \\uff1aclose when trader closes manual_close : close manually\"}},\"required\":[\"uniqueCode\",\"subPosCloseType\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-settings
        "get_copytrading_copy_settings" => RiskEndpoint {
            path: "/api/v5/copytrading/copy-settings",
            post: false,
            public: false,
            keys: &["instType", "uniqueCode"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-my-lead-traders
        "get_copytrading_current_lead_traders" => RiskEndpoint {
            path: "/api/v5/copytrading/current-lead-traders",
            post: false,
            public: false,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-trading-configuration
        "get_copytrading_public_config" => RiskEndpoint {
            path: "/api/v5/copytrading/public-config",
            post: false,
            public: true,
            keys: &["instType"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-ranks
        "get_copytrading_public_lead_traders" => RiskEndpoint {
            path: "/api/v5/copytrading/public-lead-traders",
            post: false,
            public: true,
            keys: &[
                "instType",
                "sortType",
                "state",
                "minLeadDays",
                "minAssets",
                "maxAssets",
                "minAum",
                "maxAum",
                "dataVer",
                "page",
                "limit",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"sortType\":{\"type\":\"string\",\"description\":\"Sort type overview : overview, the default value pnl : profit and loss aum : assets under management win_ratio : win ratio pnl_ratio : pnl ratio current_copy_trader_pnl : current copy trader pnl\"},\"state\":{\"type\":\"string\",\"description\":\"Lead trader state 0 : All lead traders, the default, including vacancy and non-vacancy 1 : lead traders who have vacancy\"},\"minLeadDays\":{\"type\":\"string\",\"description\":\"Minimum lead days 1 : 7 days 2 : 30 days 3 : 90 days 4 : 180 days\"},\"minAssets\":{\"type\":\"string\",\"description\":\"Minimum assets in USDT\"},\"maxAssets\":{\"type\":\"string\",\"description\":\"Maximum assets in USDT\"},\"minAum\":{\"type\":\"string\",\"description\":\"Minimum assets in USDT under management.\"},\"maxAum\":{\"type\":\"string\",\"description\":\"Maximum assets in USDT under management.\"},\"dataVer\":{\"type\":\"string\",\"description\":\"Data version. It is 14 numbers. e.g. 20231010182400. Generally, it is used for pagination A new version will be generated every 10 minutes. Only last 5 versions are stored The default is latest version. If it is not exist, error will not be throwed and the latest version will be used.\"},\"page\":{\"type\":\"string\",\"description\":\"Page for pagination\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 20; the default is 10\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-weekly-pnl
        "get_copytrading_public_weekly_pnl" => RiskEndpoint {
            path: "/api/v5/copytrading/public-weekly-pnl",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-daily-pnl
        "get_copytrading_public_pnl" => RiskEndpoint {
            path: "/api/v5/copytrading/public-pnl",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode", "lastDays"],
            required: &["uniqueCode", "lastDays"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"lastDays\":{\"type\":\"string\",\"description\":\"Last days 1 : last 7 days 2 : last 30 days 3 : last 90 days 4 : last 365 days\"}},\"required\":[\"uniqueCode\",\"lastDays\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-stats
        "get_copytrading_public_stats" => RiskEndpoint {
            path: "/api/v5/copytrading/public-stats",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode", "lastDays"],
            required: &["uniqueCode", "lastDays"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"lastDays\":{\"type\":\"string\",\"description\":\"Last days 1 : last 7 days 2 : last 30 days 3 : last 90 days 4 : last 365 days\"}},\"required\":[\"uniqueCode\",\"lastDays\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-currency-preferences
        "get_copytrading_public_preference_currency" => RiskEndpoint {
            path: "/api/v5/copytrading/public-preference-currency",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-current-lead-positions
        "get_copytrading_public_current_subpositions" => RiskEndpoint {
            path: "/api/v5/copytrading/public-current-subpositions",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode", "after", "before", "limit"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value.\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested subPosId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested subPosId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-lead-position-history
        "get_copytrading_public_subpositions_history" => RiskEndpoint {
            path: "/api/v5/copytrading/public-subpositions-history",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode", "after", "before", "limit"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value.\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested subPosId .\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested subPosId .\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-traders
        "get_copytrading_public_copy_traders" => RiskEndpoint {
            path: "/api/v5/copytrading/public-copy-traders",
            post: false,
            public: true,
            keys: &["instType", "uniqueCode", "limit"],
            required: &["uniqueCode"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instType\":{\"type\":\"string\",\"description\":\"Instrument type SWAP , the default value\"},\"uniqueCode\":{\"type\":\"string\",\"description\":\"Lead trader unique code A combination of case-sensitive alphanumerics, all numbers and the length is 16 or 18 characters, e.g. 213E8C92DC61EFAC (16 characters) or 381749205163847291 (18 characters)\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100 ; The default is 100\"}},\"required\":[\"uniqueCode\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-series
        "get_public_event_contract_series" => RiskEndpoint {
            path: "/api/v5/public/event-contract/series",
            post: false,
            public: true,
            keys: &["seriesId"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"seriesId\":{\"type\":\"string\",\"description\":\"Series ID, e.g. BTC-ABOVE-DAILY . If not passed, all series will be returned.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-events
        "get_public_event_contract_events" => RiskEndpoint {
            path: "/api/v5/public/event-contract/events",
            post: false,
            public: true,
            keys: &["seriesId", "eventId", "state", "limit", "before", "after"],
            required: &["seriesId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"seriesId\":{\"type\":\"string\",\"description\":\"Series ID, e.g. BTC-ABOVE-DAILY\"},\"eventId\":{\"type\":\"string\",\"description\":\"Event ID, e.g. BTC-ABOVE-DAILY-260224-1600\"},\"state\":{\"type\":\"string\",\"description\":\"Event state filter. preopen live settling expired\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination. Returns records newer than the requested expTime , not included.\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination. Returns records earlier than the requested expTime , not included.\"}},\"required\":[\"seriesId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-markets
        "get_public_event_contract_markets" => RiskEndpoint {
            path: "/api/v5/public/event-contract/markets",
            post: false,
            public: true,
            keys: &[
                "seriesId", "eventId", "instId", "state", "limit", "before", "after",
            ],
            required: &["seriesId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"seriesId\":{\"type\":\"string\",\"description\":\"Series ID, e.g. BTC-ABOVE-DAILY\"},\"eventId\":{\"type\":\"string\",\"description\":\"Event ID, e.g. BTC-ABOVE-DAILY-260224-1600\"},\"instId\":{\"type\":\"string\",\"description\":\"Instrument ID, e.g. BTC-ABOVE-DAILY-260224-1600-65000\"},\"state\":{\"type\":\"string\",\"description\":\"Filter by market status. preopen live settling expired\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. Maximum is 100. Default is 100.\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination. Returns records newer than the requested expTime , not included.\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination. Returns records earlier than the requested expTime , not included.\"}},\"required\":[\"seriesId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-interest-rate-and-loan-quota
        "get_public_interest_rate_loan_quota" => RiskEndpoint {
            path: "/api/v5/public/interest-rate-loan-quota",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history
        "get_asset_withdrawal_history" => RiskEndpoint {
            path: "/api/v5/asset/withdrawal-history",
            post: false,
            public: false,
            keys: &[
                "ccy", "wdId", "clientId", "txId", "type", "state", "after", "before", "limit",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Currency, e.g. BTC\"},\"wdId\":{\"type\":\"string\",\"description\":\"Withdrawal ID\"},\"clientId\":{\"type\":\"string\",\"description\":\"Client-supplied ID A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.\"},\"txId\":{\"type\":\"string\",\"description\":\"Hash record of the deposit\"},\"type\":{\"type\":\"string\",\"description\":\"Withdrawal type 3 : Internal transfer 4 : On-chain withdrawal\"},\"state\":{\"type\":\"string\",\"description\":\"Status of withdrawal Stage 1 : Pending withdrawal 19 : insufficient balance in the hot wallet 17 : Pending response from Travel Rule vendor 10 : Waiting transfer 0 : Waiting withdrawal 4 / 5 / 6 / 8 / 9 / 12 : Waiting manual review 7 : Approved > 0 , 17 , 19 can be cancelled, other statuses cannot be cancelled Stage 2 : Withdrawal in progress (Applicable to on-chain withdrawals, internal transfers do not have this stage) 1 : Broadcasting your transaction to chain 15 : Pending transaction validation 16 : Due to local laws and regulations, your withdrawal may take up to 24 hours to arrive -3 : Canceling Final stage -2 : Canceled -1 : Failed 2 : Success\"},\"after\":{\"type\":\"string\",\"description\":\"Pagination of data to return records earlier than the requested ts, Unix timestamp format in milliseconds, e.g. 1654041600000\"},\"before\":{\"type\":\"string\",\"description\":\"Pagination of data to return records newer than the requested ts, Unix timestamp format in milliseconds, e.g. 1656633600000\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100 ; The default is 100\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-payment-methods
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
        "get_account_subaccount_max_withdrawal" => RiskEndpoint {
            path: "/api/v5/account/subaccount/max-withdrawal",
            post: false,
            public: false,
            keys: &["subAcct", "ccy"],
            required: &["subAcct"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\",\"description\":\"Sub-account name\"},\"ccy\":{\"type\":\"string\",\"description\":\"Single currency or multiple currencies (no more than 20) separated with comma, e.g. BTC or BTC,ETH .\"}},\"required\":[\"subAcct\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-history-of-managed-sub-account-transfer
        "get_asset_subaccount_managed_subaccount_bills" => RiskEndpoint {
            path: "/api/v5/asset/subaccount/managed-subaccount-bills",
            post: false,
            public: false,
            keys: &[
                "ccy", "type", "subAcct", "subUid", "after", "before", "limit",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Currency, e.g BTC\"},\"type\":{\"type\":\"string\",\"description\":\"Transfer type 0 : Transfers from master account to sub-account 1 : Transfers from sub-account to master account\"},\"subAcct\":{\"type\":\"string\",\"description\":\"Sub-account name\"},\"subUid\":{\"type\":\"string\",\"description\":\"Sub-account UID\"},\"after\":{\"type\":\"string\",\"description\":\"Query the data prior to the requested bill ID creation time (exclude), Unix timestamp in millisecond format, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Query the data after the requested bill ID creation time (exclude), Unix timestamp in millisecond format, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-product-info
        "get_finance_stable_rewards_product_info" => RiskEndpoint {
            path: "/api/v5/finance/stable-rewards/product-info",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Stablecoin, e.g. USDG\"}},\"required\":[\"ccy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-balance
        "get_finance_stable_rewards_balance" => RiskEndpoint {
            path: "/api/v5/finance/stable-rewards/balance",
            post: false,
            public: false,
            keys: &["ccy"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Stablecoin, e.g. USDG Returns all supported stablecoins if not specified\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-apy-history
        "get_finance_stable_rewards_apy_history" => RiskEndpoint {
            path: "/api/v5/finance/stable-rewards/apy-history",
            post: false,
            public: false,
            keys: &["ccy", "days"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Stablecoin, e.g. USDG\"},\"days\":{\"type\":\"string\",\"description\":\"Number of historical days to return. The default is 100 . The maximum is 100\"}},\"required\":[\"ccy\"]}",
            ),
        },
        _ => return None,
    })
}
