//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
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
        _ => return None,
    })
}
