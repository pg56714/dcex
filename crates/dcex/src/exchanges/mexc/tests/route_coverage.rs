//! Route coverage for every MEXC dispatch name against the official REST docs
//! (https://www.mexc.com/api-docs/spot-v3/ and https://www.mexc.com/api-docs/futures/),
//! exercised through a local server.

use std::collections::{BTreeSet, HashMap};
use std::time::Duration;

use super::MexcClient;

/// Rows: (public, method name, params, HTTP method, path).
#[allow(clippy::type_complexity)]
const ROUTE_CASES: &[(bool, &str, &[(&str, &str)], &str, &str)] = &[
    (
        false,
        "close_spot_listen_key",
        &[("listenKey", "test-key")],
        "DELETE",
        "/api/v3/userDataStream",
    ),
    (
        false,
        "keep_alive_spot_listen_key",
        &[("listenKey", "test-key")],
        "PUT",
        "/api/v3/userDataStream",
    ),
    (
        false,
        "get_spot_listen_keys",
        &[],
        "GET",
        "/api/v3/userDataStream",
    ),
    (
        false,
        "create_spot_listen_key",
        &[],
        "POST",
        "/api/v3/userDataStream",
    ),
    (
        false,
        "create_deposit_address",
        &[("coin", "USDT"), ("network", "TRC20")],
        "POST",
        "/api/v3/capital/deposit/address",
    ),
    (
        false,
        "delete_sub_account_api_key",
        &[
            ("subAccount", "sub1"),
            ("apiKey", "test-key"),
            ("recvWindow", "5000"),
        ],
        "DELETE",
        "/api/v3/sub-account/apiKey",
    ),
    (
        false,
        "create_sub_account_api_key",
        &[
            ("subAccount", "sub1"),
            ("note", "trading"),
            ("permissions", "SPOT_ACCOUNT_READ"),
            ("ip", "127.0.0.1"),
            ("recvWindow", "5000"),
        ],
        "POST",
        "/api/v3/sub-account/apiKey",
    ),
    (
        false,
        "get_sub_account_api_keys",
        &[("subAccount", "sub1"), ("recvWindow", "5000")],
        "GET",
        "/api/v3/sub-account/apiKey",
    ),
    (
        false,
        "get_stp_strategy_group",
        &[("tradeGroupName", "group1")],
        "GET",
        "/api/v3/strategy/group",
    ),
    (
        false,
        "remove_stp_strategy_group_members",
        &[("uid", "1001,1002"), ("tradeGroupId", "91")],
        "DELETE",
        "/api/v3/strategy/group/uid",
    ),
    (
        false,
        "get_withdrawal_addresses",
        &[("coin", "USDT"), ("page", "1"), ("limit", "1")],
        "GET",
        "/api/v3/capital/withdraw/address",
    ),
    (
        false,
        "delete_stp_strategy_group",
        &[("tradeGroupId", "91")],
        "DELETE",
        "/api/v3/strategy/group",
    ),
    (
        false,
        "create_stp_strategy_group",
        &[("tradeGroupName", "group1")],
        "POST",
        "/api/v3/strategy/group",
    ),
    (
        false,
        "add_stp_strategy_group_members",
        &[("uid", "1001,1002"), ("tradeGroupId", "91")],
        "POST",
        "/api/v3/strategy/group/uid",
    ),
    (
        true,
        "get_spot_offline_symbols",
        &[],
        "GET",
        "/api/v3/symbol/offline",
    ),
    (
        true,
        "get_announcements",
        &[("language", "en-US"), ("page", "1"), ("limit", "20")],
        "GET",
        "/api/v3/announcements",
    ),
    (
        true,
        "get_contract_supported_currencies",
        &[],
        "GET",
        "/api/v1/contract/support_currencies",
    ),
    (false, "get_uid", &[], "GET", "/api/v3/uid"),
    (
        false,
        "get_api_key_info",
        &[("accessKey", "query-key")],
        "GET",
        "/api/v3/apiKeyInfo",
    ),
    (
        false,
        "set_api_key_ip_whitelist",
        &[
            ("apiKey", "query-key"),
            ("ipWhiteList", "127.0.0.1,192.0.2.1"),
            ("note", "trading"),
        ],
        "POST",
        "/api/v3/apiKeyInfo",
    ),
    (
        false,
        "get_convertible_assets",
        &[],
        "GET",
        "/api/v3/capital/convert/list",
    ),
    (
        false,
        "convert_dust",
        &[("asset", "BTC,ETH")],
        "POST",
        "/api/v3/capital/convert",
    ),
    (
        false,
        "get_dust_conversion_history",
        &[
            ("startTime", "1700000000000"),
            ("endTime", "1700000010000"),
            ("page", "1"),
            ("limit", "100"),
        ],
        "GET",
        "/api/v3/capital/convert",
    ),
    (
        false,
        "create_sub_account",
        &[
            ("subAccount", "sub1"),
            ("note", "trading"),
            ("recvWindow", "5000"),
        ],
        "POST",
        "/api/v3/sub-account/virtualSubAccount",
    ),
    (
        false,
        "get_contract_profit_rate",
        &[("type", "1")],
        "GET",
        "/api/v1/private/account/profit_rate/1",
    ),
    (
        false,
        "get_contract_fee_deduction_config",
        &[],
        "GET",
        "/api/v1/private/account/feeDeductConfigs",
    ),
    (
        false,
        "get_contract_fee_discount_config",
        &[],
        "GET",
        "/api/v1/private/account/config/contractFeeDiscountConfig",
    ),
    (
        false,
        "get_contract_discount_usage",
        &[],
        "GET",
        "/api/v1/private/account/discountType",
    ),
    (
        false,
        "cancel_contract_batch_orders_by_external_id",
        &[(
            "orders",
            "[{\"product_symbol\":\"BTC-USDT-SWAP\",\"externalOid\":\"1\"},{\"product_symbol\":\"ETH-USDT-SWAP\",\"externalOid\":\"2\"}]",
        )],
        "POST",
        "/api/v1/private/order/batch_cancel_with_external",
    ),
    (
        false,
        "get_contract_batch_orders_by_external_id",
        &[(
            "orders",
            "[{\"product_symbol\":\"BTC-USDT-SWAP\",\"externalOid\":\"1\"},{\"product_symbol\":\"ETH-USDT-SWAP\",\"externalOid\":\"2\"}]",
        )],
        "POST",
        "/api/v1/private/order/batch_query_with_external",
    ),
    (
        false,
        "get_contract_closed_orders",
        &[("product_symbol", "BTC-USDT-SWAP"), ("page_size", "10")],
        "GET",
        "/api/v1/private/order/list/close_orders",
    ),
    (
        false,
        "get_contract_fee_details",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("page_size", "10"),
            ("ids", "11,12"),
        ],
        "GET",
        "/api/v1/private/order/fee_details",
    ),
    (
        false,
        "get_contract_30_day_fee_statistics",
        &[],
        "GET",
        "/api/v1/private/account/asset_book/order_deal_fee/total",
    ),
    (
        false,
        "cancel_spot_all_orders",
        &[("all_symbols", "true")],
        "DELETE",
        "/api/v3/order/all",
    ),
    (
        false,
        "get_contract_open_stop_orders",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/private/stoporder/open_orders",
    ),
    (true, "ping", &[], "GET", "/api/v3/ping"),
    (true, "get_spot_time", &[], "GET", "/api/v3/time"),
    (
        true,
        "get_spot_default_symbols",
        &[],
        "GET",
        "/api/v3/defaultSymbols",
    ),
    (
        true,
        "get_spot_exchange_info",
        &[],
        "GET",
        "/api/v3/exchangeInfo",
    ),
    (
        true,
        "get_spot_orderbook",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/depth",
    ),
    (
        true,
        "get_spot_recent_trades",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/trades",
    ),
    (
        true,
        "get_spot_agg_trades",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/aggTrades",
    ),
    (
        true,
        "get_spot_klines",
        &[("product_symbol", "BTC-USDT-SPOT"), ("interval", "1m")],
        "GET",
        "/api/v3/klines",
    ),
    (
        true,
        "get_spot_avg_price",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/avgPrice",
    ),
    (
        true,
        "get_spot_ticker_24hr",
        &[],
        "GET",
        "/api/v3/ticker/24hr",
    ),
    (
        true,
        "get_spot_ticker_price",
        &[],
        "GET",
        "/api/v3/ticker/price",
    ),
    (
        true,
        "get_spot_book_ticker",
        &[],
        "GET",
        "/api/v3/ticker/bookTicker",
    ),
    (false, "get_kyc_status", &[], "GET", "/api/v3/kyc/status"),
    (
        false,
        "get_spot_self_symbols",
        &[],
        "GET",
        "/api/v3/selfSymbols",
    ),
    (false, "get_spot_account", &[], "GET", "/api/v3/account"),
    (
        false,
        "get_spot_mx_deduct_status",
        &[],
        "GET",
        "/api/v3/mxDeduct/enable",
    ),
    (
        false,
        "set_spot_mx_deduct",
        &[("mxDeductEnable", "true")],
        "POST",
        "/api/v3/mxDeduct/enable",
    ),
    (
        false,
        "get_spot_symbol_commission",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/tradeFee",
    ),
    (
        false,
        "get_currency_info",
        &[],
        "GET",
        "/api/v3/capital/config/getall",
    ),
    (
        false,
        "get_deposit_history",
        &[],
        "GET",
        "/api/v3/capital/deposit/hisrec",
    ),
    (
        false,
        "get_withdraw_history",
        &[],
        "GET",
        "/api/v3/capital/withdraw/history",
    ),
    (
        false,
        "get_deposit_address",
        &[("coin", "USDT")],
        "GET",
        "/api/v3/capital/deposit/address",
    ),
    (
        false,
        "user_universal_transfer",
        &[
            ("fromAccountType", "SPOT"),
            ("toAccountType", "FUTURES"),
            ("asset", "USDT"),
            ("amount", "1"),
        ],
        "POST",
        "/api/v3/capital/transfer",
    ),
    (
        false,
        "get_user_universal_transfer_history",
        &[("fromAccountType", "SPOT"), ("toAccountType", "FUTURES")],
        "GET",
        "/api/v3/capital/transfer",
    ),
    (
        false,
        "get_user_universal_transfer_by_id",
        &[("tranId", "123")],
        "GET",
        "/api/v3/capital/transfer/tranId",
    ),
    (
        false,
        "get_internal_transfer_history",
        &[],
        "GET",
        "/api/v3/capital/transfer/internal",
    ),
    (
        false,
        "get_subaccounts",
        &[],
        "GET",
        "/api/v3/sub-account/list",
    ),
    (
        false,
        "get_subaccount_asset",
        &[("subAccount", "alpha"), ("accountType", "SPOT")],
        "GET",
        "/api/v3/sub-account/asset",
    ),
    (
        false,
        "transfer_subaccount_assets",
        &[
            ("fromAccountType", "SPOT"),
            ("toAccountType", "SPOT"),
            ("asset", "USDT"),
            ("amount", "1"),
        ],
        "POST",
        "/api/v3/capital/sub-account/universalTransfer",
    ),
    (
        false,
        "get_subaccount_transfer_history",
        &[("fromAccountType", "SPOT"), ("toAccountType", "SPOT")],
        "GET",
        "/api/v3/capital/sub-account/universalTransfer",
    ),
    (
        false,
        "test_spot_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order/test",
    ),
    (
        false,
        "place_spot_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_limit_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("side", "BUY"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_limit_buy_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_limit_sell_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_post_only_limit_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("side", "SELL"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_post_only_limit_buy_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_post_only_limit_sell_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_market_order",
        &[
            ("product_symbol", "BTC-USDT-SPOT"),
            ("side", "BUY"),
            ("quoteOrderQty", "10"),
        ],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_market_buy_order",
        &[("product_symbol", "BTC-USDT-SPOT"), ("quoteOrderQty", "10")],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_market_sell_order",
        &[("product_symbol", "BTC-USDT-SPOT"), ("quantity", "1")],
        "POST",
        "/api/v3/order",
    ),
    (
        false,
        "place_spot_batch_orders",
        &[(
            "batchOrders",
            "[{\"symbol\":\"BTCUSDT\",\"side\":\"BUY\",\"type\":\"LIMIT\",\"quantity\":\"1\",\"price\":\"1\"}]",
        )],
        "POST",
        "/api/v3/batchOrders",
    ),
    (
        false,
        "cancel_spot_order",
        &[("product_symbol", "BTC-USDT-SPOT"), ("orderId", "123")],
        "DELETE",
        "/api/v3/order",
    ),
    (
        false,
        "cancel_spot_open_orders",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "DELETE",
        "/api/v3/openOrders",
    ),
    (
        false,
        "get_spot_order",
        &[("product_symbol", "BTC-USDT-SPOT"), ("orderId", "123")],
        "GET",
        "/api/v3/order",
    ),
    (
        false,
        "get_spot_open_orders",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/openOrders",
    ),
    (
        false,
        "get_spot_all_orders",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/allOrders",
    ),
    (
        false,
        "get_spot_my_trades",
        &[("product_symbol", "BTC-USDT-SPOT")],
        "GET",
        "/api/v3/myTrades",
    ),
    (
        true,
        "get_contract_time",
        &[],
        "GET",
        "/api/v1/contract/ping",
    ),
    (
        true,
        "get_contract_details",
        &[],
        "GET",
        "/api/v1/contract/detail/country",
    ),
    (
        true,
        "get_contract_ticker",
        &[],
        "GET",
        "/api/v1/contract/ticker",
    ),
    (
        true,
        "get_contract_depth",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/depth/BTC_USDT",
    ),
    (
        true,
        "get_contract_depth_commits",
        &[("product_symbol", "BTC-USDT-SWAP"), ("limit", "20")],
        "GET",
        "/api/v1/contract/depth_commits/BTC_USDT/20",
    ),
    (
        true,
        "get_contract_index_price",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/index_price/BTC_USDT",
    ),
    (
        true,
        "get_contract_fair_price",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/fair_price/BTC_USDT",
    ),
    (
        true,
        "get_contract_funding_rate",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/funding_rate/BTC_USDT",
    ),
    (
        true,
        "get_contract_kline",
        &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "Min1")],
        "GET",
        "/api/v1/contract/kline/BTC_USDT",
    ),
    (
        true,
        "get_contract_index_price_kline",
        &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "Min1")],
        "GET",
        "/api/v1/contract/kline/index_price/BTC_USDT",
    ),
    (
        true,
        "get_contract_fair_price_kline",
        &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "Min1")],
        "GET",
        "/api/v1/contract/kline/fair_price/BTC_USDT",
    ),
    (
        true,
        "get_contract_deals",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/deals/BTC_USDT",
    ),
    (
        true,
        "get_contract_risk_reverse",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/contract/risk_reverse/BTC_USDT",
    ),
    (
        true,
        "get_contract_risk_reverse_history",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("page_num", "1"),
            ("page_size", "20"),
        ],
        "GET",
        "/api/v1/contract/risk_reverse/history",
    ),
    (
        true,
        "get_contract_funding_rate_history",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("page_num", "1"),
            ("page_size", "20"),
        ],
        "GET",
        "/api/v1/contract/funding_rate/history",
    ),
    (
        false,
        "get_contract_assets",
        &[],
        "GET",
        "/api/v1/private/account/assets",
    ),
    (
        false,
        "get_contract_asset",
        &[("currency", "USDT")],
        "GET",
        "/api/v1/private/account/asset/USDT",
    ),
    (
        false,
        "get_contract_transfer_records",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/account/transfer_record",
    ),
    (
        false,
        "get_contract_history_positions",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/position/list/history_positions",
    ),
    (
        false,
        "get_contract_open_positions",
        &[],
        "GET",
        "/api/v1/private/position/open_positions",
    ),
    (
        false,
        "get_contract_funding_records",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/position/funding_records",
    ),
    (
        false,
        "get_contract_risk_limits",
        &[],
        "GET",
        "/api/v1/private/account/risk_limit",
    ),
    (
        false,
        "get_contract_trading_fee_rate",
        &[],
        "GET",
        "/api/v1/private/account/tiered_fee_rate/v2",
    ),
    (
        false,
        "get_contract_leverage",
        &[("product_symbol", "BTC-USDT-SWAP")],
        "GET",
        "/api/v1/private/position/leverage",
    ),
    (
        false,
        "change_contract_margin",
        &[("positionId", "7"), ("amount", "1"), ("type", "ADD")],
        "POST",
        "/api/v1/private/position/change_margin",
    ),
    (
        false,
        "change_contract_auto_add_margin",
        &[("positionId", "7"), ("isEnabled", "true")],
        "POST",
        "/api/v1/private/position/change_auto_add_im",
    ),
    (
        false,
        "change_contract_leverage",
        &[("leverage", "5"), ("positionId", "7")],
        "POST",
        "/api/v1/private/position/change_leverage",
    ),
    (
        false,
        "get_contract_position_mode",
        &[],
        "GET",
        "/api/v1/private/position/position_mode",
    ),
    (
        false,
        "change_contract_position_mode",
        &[("positionMode", "1")],
        "POST",
        "/api/v1/private/position/change_position_mode",
    ),
    (
        false,
        "change_contract_multi_asset_mode",
        &[("isMultiAssetMode", "true")],
        "POST",
        "/api/v1/private/multiAssets/changeMultiAssetMode/true",
    ),
    (
        false,
        "place_contract_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "1"),
            ("type", "1"),
            ("openType", "1"),
            ("vol", "1"),
            ("price", "1"),
            ("leverage", "5"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_limit_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "1"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_limit_buy_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_limit_sell_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_post_only_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "3"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_post_only_buy_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_post_only_sell_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("price", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_market_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "1"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_market_buy_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "place_contract_market_sell_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("vol", "1"),
            ("leverage", "50"),
            ("openType", "2"),
        ],
        "POST",
        "/api/v1/private/order/create",
    ),
    (
        false,
        "cancel_contract_orders",
        &[("orders", "[\"1\",\"2\"]")],
        "POST",
        "/api/v1/private/order/cancel",
    ),
    (
        false,
        "cancel_contract_order",
        &[("order_id", "1")],
        "POST",
        "/api/v1/private/order/cancel",
    ),
    (
        false,
        "cancel_contract_order_with_external_id",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("externalOid", "ext-1"),
        ],
        "POST",
        "/api/v1/private/order/cancel_with_external",
    ),
    (
        false,
        "cancel_all_contract_orders",
        &[],
        "POST",
        "/api/v1/private/order/cancel_all",
    ),
    (
        false,
        "amend_contract_limit_order",
        &[("orderId", "1"), ("price", "2"), ("vol", "1")],
        "POST",
        "/api/v1/private/order/change_limit_order",
    ),
    (
        false,
        "chase_contract_limit_order",
        &[("orderId", "1")],
        "POST",
        "/api/v1/private/order/chase_limit_order",
    ),
    (
        false,
        "get_contract_open_order_count",
        &[],
        "POST",
        "/api/v1/private/order/open_order_total_count",
    ),
    (
        false,
        "reverse_contract_position",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("positionId", "7"),
            ("vol", "1"),
        ],
        "POST",
        "/api/v1/private/position/reverse",
    ),
    (
        false,
        "close_all_contract_positions",
        &[],
        "POST",
        "/api/v1/private/position/close_all",
    ),
    (
        false,
        "get_contract_open_orders",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/order/list/open_orders",
    ),
    (
        false,
        "get_contract_history_orders",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/order/list/history_orders",
    ),
    (
        false,
        "get_contract_order_by_external_id",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("external_oid", "ext-1"),
        ],
        "GET",
        "/api/v1/private/order/external/BTC_USDT/ext-1",
    ),
    (
        false,
        "get_contract_order",
        &[("order_id", "123")],
        "GET",
        "/api/v1/private/order/get/123",
    ),
    (
        false,
        "get_contract_orders",
        &[("order_ids", "[\"1\",\"2\"]")],
        "GET",
        "/api/v1/private/order/batch_query",
    ),
    (
        false,
        "get_contract_order_deal_details",
        &[("order_id", "123")],
        "GET",
        "/api/v1/private/order/deal_details/123",
    ),
    (
        false,
        "get_contract_order_deals",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("page_num", "1"),
            ("page_size", "20"),
        ],
        "GET",
        "/api/v1/private/order/list/order_deals/v3",
    ),
    (
        false,
        "get_contract_plan_orders",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/planorder/list/orders",
    ),
    (
        false,
        "place_contract_plan_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("vol", "1"),
            ("side", "1"),
            ("openType", "1"),
            ("triggerPrice", "100"),
            ("triggerType", "1"),
            ("executeCycle", "1"),
            ("orderType", "5"),
            ("trend", "1"),
            ("leverage", "5"),
        ],
        "POST",
        "/api/v1/private/planorder/place/v2",
    ),
    (
        false,
        "amend_contract_plan_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("orderId", "1"),
            ("triggerPrice", "100"),
            ("price", "99"),
            ("orderType", "1"),
            ("triggerType", "1"),
            ("trend", "1"),
            ("from", "1"),
        ],
        "POST",
        "/api/v1/private/planorder/change_price",
    ),
    (
        false,
        "cancel_contract_plan_orders",
        &[("orders", "[{\"symbol\":\"BTC_USDT\",\"orderId\":\"1\"}]")],
        "POST",
        "/api/v1/private/planorder/cancel",
    ),
    (
        false,
        "cancel_all_contract_plan_orders",
        &[],
        "POST",
        "/api/v1/private/planorder/cancel_all",
    ),
    (
        false,
        "get_contract_stop_orders",
        &[("page_num", "1"), ("page_size", "20")],
        "GET",
        "/api/v1/private/stoporder/list/orders",
    ),
    (
        false,
        "place_contract_position_tpsl",
        &[
            ("lossTrend", "1"),
            ("profitTrend", "1"),
            ("positionId", "7"),
            ("vol", "1"),
            ("stopLossPrice", "90"),
            ("takeProfitPrice", "110"),
        ],
        "POST",
        "/api/v1/private/stoporder/place",
    ),
    (
        false,
        "cancel_contract_tpsl_orders",
        &[("orders", "[{\"stopPlanOrderId\":\"1\"}]")],
        "POST",
        "/api/v1/private/stoporder/cancel",
    ),
    (
        false,
        "cancel_all_contract_tpsl_orders",
        &[],
        "POST",
        "/api/v1/private/stoporder/cancel_all",
    ),
    (
        false,
        "amend_contract_limit_tpsl",
        &[("orderId", "1"), ("stopLossPrice", "90")],
        "POST",
        "/api/v1/private/stoporder/change_price",
    ),
    (
        false,
        "amend_contract_tpsl_order",
        &[("stopPlanOrderId", "1"), ("stopLossPrice", "90")],
        "POST",
        "/api/v1/private/stoporder/change_plan_price",
    ),
    (
        false,
        "amend_contract_plan_tpsl",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("orderId", "1"),
            ("stopLossPrice", "90"),
        ],
        "POST",
        "/api/v1/private/planorder/change_stop_order",
    ),
    (
        false,
        "place_contract_trailing_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("leverage", "5"),
            ("side", "1"),
            ("vol", "1"),
            ("openType", "1"),
            ("trend", "1"),
            ("backType", "1"),
            ("backValue", "0.01"),
            ("positionMode", "1"),
        ],
        "POST",
        "/api/v1/private/trackorder/place",
    ),
    (
        false,
        "cancel_contract_trailing_order",
        &[("trackOrderId", "1")],
        "POST",
        "/api/v1/private/trackorder/cancel",
    ),
    (
        false,
        "amend_contract_trailing_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("trackOrderId", "1"),
            ("trend", "1"),
            ("backType", "1"),
            ("backValue", "0.02"),
            ("vol", "1"),
        ],
        "POST",
        "/api/v1/private/trackorder/change_order",
    ),
    (
        false,
        "get_contract_trailing_orders",
        &[("states", "[0,1]")],
        "GET",
        "/api/v1/private/trackorder/list/orders",
    ),
];

struct Captured {
    head: String,
    body: String,
}

impl Captured {
    fn request_line(&self) -> &str {
        self.head.lines().next().unwrap_or_default()
    }

    fn header(&self, name: &str) -> Option<&str> {
        self.head.lines().skip(1).find_map(|line| {
            let (key, value) = line.split_once(':')?;
            key.trim()
                .eq_ignore_ascii_case(name)
                .then_some(value.trim())
        })
    }
}

fn read_request(stream: &mut std::net::TcpStream) -> Captured {
    use std::io::Read;

    let mut data = Vec::new();
    let mut buffer = [0u8; 4096];
    loop {
        let size = stream.read(&mut buffer).expect("read");
        if size == 0 {
            break;
        }
        data.extend_from_slice(&buffer[..size]);
        let text = String::from_utf8_lossy(&data);
        if let Some(end) = text.find("\r\n\r\n") {
            let length = text[..end]
                .lines()
                .find_map(|line| {
                    let (name, value) = line.split_once(':')?;
                    if name.eq_ignore_ascii_case("content-length") {
                        value.trim().parse::<usize>().ok()
                    } else {
                        None
                    }
                })
                .unwrap_or(0);
            if data.len() >= end + 4 + length {
                break;
            }
        }
    }
    let text = String::from_utf8_lossy(&data).into_owned();
    let (head, body) = text.split_once("\r\n\r\n").unwrap_or((text.as_str(), ""));
    Captured {
        head: head.to_string(),
        body: body.to_string(),
    }
}

/// Serves until the endpoint request arrives; signer clock-sync calls to
/// `/api/v3/time` are answered and skipped unless `path_is_time` is set.
fn serve_endpoint(path_is_time: bool) -> (String, std::thread::JoinHandle<Captured>) {
    use std::io::Write;
    use std::net::TcpListener;

    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let handle = std::thread::spawn(move || {
        loop {
            let (mut stream, _) = listener.accept().expect("accept");
            let captured = read_request(&mut stream);
            let is_time = captured.request_line().starts_with("GET /api/v3/time ");
            let body = if is_time {
                format!(
                    r#"{{"serverTime":{}}}"#,
                    std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .expect("clock")
                        .as_millis()
                )
            } else if captured.request_line().contains(" /api/v1/") {
                r#"{"success":true,"code":0,"data":[]}"#.to_string()
            } else {
                "{}".to_string()
            };
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            )
            .expect("write");
            if !is_time || path_is_time {
                return captured;
            }
        }
    });
    (url, handle)
}

fn client_for(url: String) -> MexcClient {
    MexcClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(2),
        url.clone(),
        url,
    )
    .expect("client")
}

fn pairs(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect()
}

fn run_case(public: bool, method: &str, params: &[(&str, &str)], path: &str) -> Captured {
    let (url, server) = serve_endpoint(path == "/api/v3/time");
    let client = client_for(url);
    let params = pairs(params);
    let method_name = method.to_string();
    crate::http::block_on(async move {
        if public {
            client.public_request(&method_name, params).await
        } else {
            client.private_request(&method_name, params).await
        }
    })
    .unwrap_or_else(|error| panic!("{method}: {error}"));
    server.join().expect("server")
}

#[test]
fn every_dispatch_name_uses_official_route() {
    for (public, method, params, http_method, path) in ROUTE_CASES {
        let captured = run_case(*public, method, params, path);
        let request_line = captured.request_line();
        let expected = format!("{http_method} {path}");
        assert!(
            request_line == format!("{expected} HTTP/1.1")
                || request_line.starts_with(&format!("{expected}?")),
            "{method}: {request_line}"
        );
        if *public {
            assert!(captured.header("X-MEXC-APIKEY").is_none(), "{method}");
            assert!(captured.header("Signature").is_none(), "{method}");
        } else if path.starts_with("/api/v3/") {
            assert_eq!(
                captured.header("X-MEXC-APIKEY"),
                Some("api-key"),
                "{method}"
            );
            let signed =
                request_line.contains("signature=") || captured.body.contains("signature=");
            assert!(signed, "{method} must carry a signature");
        } else {
            assert_eq!(captured.header("ApiKey"), Some("api-key"), "{method}");
            assert!(captured.header("Signature").is_some(), "{method}");
            assert!(captured.header("Request-Time").is_some(), "{method}");
        }
    }
}

#[test]
fn route_cases_cover_every_dispatch_name() {
    let source = [
        include_str!("../market.rs"),
        include_str!("../account.rs"),
        include_str!("../trade.rs"),
    ]
    .join("\n");
    let mut names = BTreeSet::new();
    for line in source.lines() {
        let trimmed = line.trim_start();
        if !trimmed.starts_with('"') || !trimmed.contains("=>") {
            continue;
        }
        let arm = trimmed.split("=>").next().unwrap_or_default();
        for part in arm.split('|') {
            let name = part.trim().trim_matches('"');
            if !name.is_empty()
                && name.contains('_')
                && name
                    .chars()
                    .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_')
            {
                names.insert(name.to_string());
            }
        }
    }
    // Multi-line match arms (`"a"\n | "b" => ...`) are collected from `|` lines too.
    for line in source.lines() {
        let trimmed = line.trim_start();
        if let Some(rest) = trimmed.strip_prefix("| \"") {
            if let Some(name) = rest.split('"').next() {
                names.insert(name.to_string());
            }
        }
    }
    names.insert("ping".to_string());
    assert!(
        names.len() >= 110,
        "parsed only {} dispatch names",
        names.len()
    );
    let covered: BTreeSet<String> = ROUTE_CASES
        .iter()
        .map(|(_, method, ..)| method.to_string())
        .collect();
    let missing: Vec<_> = names.difference(&covered).collect();
    assert!(
        missing.is_empty(),
        "dispatch names without route cases: {missing:?}"
    );
}

#[test]
fn spot_post_only_order_uses_limit_maker() {
    let captured = run_case(
        false,
        "place_spot_post_only_limit_sell_order",
        &[
            ("product_symbol", "ETH-USDT-SPOT"),
            ("quantity", "0.5"),
            ("price", "2000"),
        ],
        "/api/v3/order",
    );
    let target = captured
        .request_line()
        .split_whitespace()
        .nth(1)
        .unwrap_or_default()
        .to_string();
    let query = target.split_once('?').map(|(_, q)| q).unwrap_or_default();
    let encoded = format!("{query}&{}", captured.body);
    let fields: HashMap<_, _> = encoded
        .split('&')
        .filter_map(|pair| pair.split_once('='))
        .collect();
    assert_eq!(fields.get("symbol"), Some(&"ETHUSDT"));
    assert_eq!(fields.get("side"), Some(&"SELL"));
    assert_eq!(fields.get("type"), Some(&"LIMIT_MAKER"));
    assert_eq!(fields.get("quantity"), Some(&"0.5"));
    assert_eq!(fields.get("price"), Some(&"2000"));
}

#[test]
fn contract_limit_order_json_body_matches_docs() {
    let captured = run_case(
        false,
        "place_contract_limit_buy_order",
        &[
            ("product_symbol", "ETH-USDT-SWAP"),
            ("price", "2000"),
            ("vol", "3"),
            ("openType", "2"),
            ("leverage", "5"),
        ],
        "/api/v1/private/order/create",
    );
    let body: serde_json::Value = serde_json::from_str(&captured.body).expect("json body");
    assert_eq!(body["symbol"], "ETH_USDT");
    assert_eq!(body["type"].to_string().trim_matches('"'), "1");
    assert_eq!(body["side"].to_string().trim_matches('"'), "1");
    assert_eq!(body["price"].to_string().trim_matches('"'), "2000");
    assert_eq!(body["vol"].to_string().trim_matches('"'), "3");
}

#[test]
fn contract_batch_query_joins_order_ids() {
    let captured = run_case(
        false,
        "get_contract_orders",
        &[("order_ids", r#"["1","2","3"]"#)],
        "/api/v1/private/order/batch_query",
    );
    assert!(
        captured
            .request_line()
            .starts_with("GET /api/v1/private/order/batch_query?order_ids=1%2C2%2C3 "),
        "{}",
        captured.request_line()
    );
}

#[test]
fn unknown_dispatch_names_are_rejected_before_transport() {
    let public_client = MexcClient::public(Duration::from_secs(1)).expect("client");
    let error =
        crate::http::block_on(
            async move { public_client.public_request("get_nope", Vec::new()).await },
        )
        .expect_err("unknown public");
    assert!(error.to_string().contains("unsupported MEXC public method"));
    let private_client = MexcClient::public(Duration::from_secs(1)).expect("client");
    let error = crate::http::block_on(async move {
        private_client
            .private_request("place_nope", Vec::new())
            .await
    })
    .expect_err("unknown private");
    assert!(
        error
            .to_string()
            .contains("unsupported MEXC private method")
    );
}

#[test]
fn trailing_order_states_are_sent_comma_separated() {
    for states in ["[0,1]", "0,1"] {
        let captured = run_case(
            false,
            "get_contract_trailing_orders",
            &[("states", states)],
            "/api/v1/private/trackorder/list/orders",
        );
        assert!(
            captured
                .request_line()
                .starts_with("GET /api/v1/private/trackorder/list/orders?states=0%2C1"),
            "{}",
            captured.request_line()
        );
    }
}

#[test]
fn contract_opening_orders_require_explicit_leverage() {
    // Clients use an unroutable base URL: validation must fail before transport.
    let cases: &[(&str, &[(&str, &str)])] = &[
        (
            "place_contract_order",
            &[("side", "1"), ("type", "5"), ("openType", "2")],
        ),
        (
            "place_contract_order",
            &[
                ("side", "3"),
                ("type", "5"),
                ("openType", "1"),
                ("leverage", ""),
            ],
        ),
        (
            "place_contract_limit_order",
            &[("side", "1"), ("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_limit_buy_order",
            &[("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_limit_sell_order",
            &[("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_post_only_order",
            &[("side", "3"), ("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_post_only_buy_order",
            &[("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_post_only_sell_order",
            &[("price", "1"), ("openType", "2")],
        ),
        (
            "place_contract_market_order",
            &[("side", "1"), ("openType", "2")],
        ),
        ("place_contract_market_buy_order", &[("openType", "2")]),
        ("place_contract_market_sell_order", &[("openType", "1")]),
    ];
    for (method, extra) in cases {
        let mut params = pairs(&[("product_symbol", "BTC-USDT-SWAP"), ("vol", "1")]);
        params.extend(pairs(extra));
        let client = client_for("http://127.0.0.1:9".to_string());
        let method_name = method.to_string();
        let error =
            crate::http::block_on(
                async move { client.private_request(&method_name, params).await },
            )
            .expect_err("leverage is required when opening");
        assert!(error.to_string().contains("leverage"), "{method}: {error}");
    }
}

#[test]
fn contract_closing_orders_do_not_require_leverage() {
    let captured = run_case(
        false,
        "place_contract_market_order",
        &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "4"),
            ("vol", "1"),
            ("openType", "2"),
        ],
        "/api/v1/private/order/create",
    );
    let body: serde_json::Value = serde_json::from_str(&captured.body).expect("json body");
    assert_eq!(body["side"], 4);
    assert!(body.get("leverage").is_none(), "{body}");
}
