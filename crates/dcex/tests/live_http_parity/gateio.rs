use std::time::Duration;

use dcex::exchanges::gateio::GateioClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
async fn gateio_public_live_parity() -> dcex::Result<()> {
    let client = GateioClient::new(None, None, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_all_futures_contracts", &[]),
            Case::new(
                "get_a_single_futures_contract",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_order_book",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new(
                "get_contract_kline",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new(
                "get_contract_list_tickers",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_funding_rate_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "2")],
            ),
            Case::new(
                "get_futures_contract_stats",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_all_delivery_contracts", &[]),
            Case::new("get_spot_all_currency_pairs", &[]),
            Case::new(
                "get_spot_order_book",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_kline",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new(
                "get_spot_list_tickers",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_all_delivery_contracts,
                        get_all_futures_contracts,
                        get_a_single_futures_contract,
                        get_contract_kline,
                        get_contract_list_tickers,
                        get_contract_order_book,
                        get_futures_contract_stats,
                        get_futures_funding_rate_history,
                        get_spot_all_currency_pairs,
                        get_spot_kline,
                        get_spot_list_tickers,
                        get_spot_order_book,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
async fn gateio_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["GATEIO_API_KEY", "GATEIO_API_SECRET"]) else {
        return Ok(());
    };
    let client = GateioClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["GATEIO_API_KEY", "GATEIO_API_SECRET"],
        vec![
            Case::new("get_total_balance", &[("currency", "USDT")]),
            Case::new("get_unified_accounts", &[]),
            Case::new("get_futures_account", &[]),
            Case::new("get_futures_account_book", &[("limit", "10")]),
            Case::new("get_delivery_account", &[]),
            Case::new("get_delivery_account_book", &[("limit", "10")]),
            Case::new("get_spot_account", &[("ccy", "USDT")]),
            Case::new("get_spot_account_book", &[("limit", "10")]),
            Case::new("get_spot_fee", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_batch_fee",
                &[("product_symbols", r#"["BTC-USDT-SPOT","ETH-USDT-SPOT"]"#)],
            ),
            Case::new(
                "get_futures_all_positions",
                &[("holding", "false"), ("limit", "10")],
            ),
            Case::new(
                "get_contract_single_positions",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_contract_order_list",
                &[
                    ("status", "open"),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("limit", "10"),
                ],
            ),
            Case::new(
                "get_trading_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "10")],
            ),
            Case::new(
                "get_futures_position_close_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "10")],
            ),
            Case::new(
                "get_futures_auto_deleveraging_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "10")],
            ),
            Case::new("get_delivery_all_positions", &[]),
            Case::new("get_spot_open_orders", &[("limit", "10")]),
            Case::new(
                "get_spot_order_list",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("status", "open"),
                    ("limit", "10"),
                ],
            ),
            Case::new(
                "get_spot_trading_history",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "10")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_contract_order_list,
                        get_contract_single_positions,
                        get_delivery_account,
                        get_delivery_account_book,
                        get_delivery_all_positions,
                        get_futures_account,
                        get_futures_account_book,
                        get_futures_all_positions,
                        get_futures_auto_deleveraging_history,
                        get_futures_position_close_history,
                        get_spot_account,
                        get_spot_account_book,
                        get_spot_batch_fee,
                        get_spot_fee,
                        get_spot_open_orders,
                        get_spot_order_list,
                        get_spot_trading_history,
                        get_total_balance,
                        get_trading_history,
                        get_unified_accounts,
                    ]
                )
            }
        },
    )
    .await
}
