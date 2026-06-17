use std::time::Duration;

use dcex::exchanges::mexc::MexcClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
async fn mexc_public_live_parity() -> dcex::Result<()> {
    let client = MexcClient::new(None, None, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("ping", &[]),
            Case::new("get_spot_time", &[]),
            Case::new("get_spot_default_symbols", &[]),
            Case::new(
                "get_spot_exchange_info",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_recent_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "2")],
            ),
            Case::new(
                "get_spot_agg_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "2")],
            ),
            Case::new(
                "get_spot_klines",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new("get_spot_avg_price", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_spot_ticker_24hr", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_ticker_price",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new("get_spot_book_ticker", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_contract_time", &[]),
            Case::new("get_contract_details", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_contract_ticker", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_contract_depth",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new(
                "get_contract_depth_commits",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new(
                "get_contract_index_price",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_fair_price",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_funding_rate",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_kline",
                &[("product_symbol", BTC_USDT_SWAP), ("interval", "Min1")],
            ),
            Case::new(
                "get_contract_index_price_kline",
                &[("product_symbol", BTC_USDT_SWAP), ("interval", "Min1")],
            ),
            Case::new(
                "get_contract_fair_price_kline",
                &[("product_symbol", BTC_USDT_SWAP), ("interval", "Min1")],
            ),
            Case::new(
                "get_contract_deals",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "2")],
            ),
            Case::new("get_contract_risk_reverse", &[]),
            Case::new(
                "get_contract_risk_reverse_history",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "2"),
                ],
            ),
            Case::new(
                "get_contract_funding_rate_history",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "2"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { client.public_request(case.method, case.params).await }
        },
    )
    .await
}

#[tokio::test]
async fn mexc_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["MEXC_API_KEY", "MEXC_API_SECRET"]) else {
        return Ok(());
    };
    let client = MexcClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["MEXC_API_KEY", "MEXC_API_SECRET"],
        vec![
            Case::new("get_kyc_status", &[]),
            Case::new("get_spot_self_symbols", &[]),
            Case::new("get_spot_account", &[]),
            Case::new("get_spot_mx_deduct_status", &[]),
            Case::new(
                "get_spot_symbol_commission",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new("get_currency_info", &[("coin", "USDT")]),
            Case::new("get_deposit_history", &[("coin", "USDT"), ("limit", "10")]),
            Case::new("get_withdraw_history", &[("coin", "USDT"), ("limit", "10")]),
            Case::new("get_deposit_address", &[("coin", "USDT")]),
            Case::new(
                "get_user_universal_transfer_history",
                &[
                    ("fromAccountType", "SPOT"),
                    ("toAccountType", "FUTURES"),
                    ("page", "1"),
                    ("size", "10"),
                ],
            ),
            Case::new(
                "get_user_universal_transfer_history",
                &[
                    ("fromAccountType", "FUTURES"),
                    ("toAccountType", "SPOT"),
                    ("page", "1"),
                    ("size", "10"),
                ],
            ),
            Case::new(
                "get_internal_transfer_history",
                &[("page", "1"), ("limit", "10")],
            ),
            Case::new(
                "get_contract_transfer_records",
                &[("currency", "USDT"), ("page_num", "1"), ("page_size", "10")],
            ),
            Case::new("get_contract_assets", &[]),
            Case::new("get_contract_asset", &[("currency", "USDT")]),
            Case::new(
                "get_contract_history_positions",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_open_positions",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_funding_records",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_risk_limits",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_trading_fee_rate",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_leverage",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_contract_position_mode", &[]),
            Case::new("get_spot_open_orders", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_all_orders",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "10")],
            ),
            Case::new(
                "get_spot_my_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "10")],
            ),
            Case::new(
                "get_contract_open_orders",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_history_orders",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_order_deals",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_plan_orders",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
            Case::new(
                "get_contract_stop_orders",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("page_num", "1"),
                    ("page_size", "10"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { client.private_request(case.method, case.params).await }
        },
    )
    .await
}
