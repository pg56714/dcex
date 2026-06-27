use std::time::Duration;

use dcex::exchanges::backpack::BackpackClient;

use super::common::{require_env, run_cases, run_private_cases, Case};

const BTC_USDC_SPOT: &str = "BTC-USDC-SPOT";
const BTC_USDC_SWAP: &str = "BTC-USDC-SWAP";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn backpack_public_live_parity() -> dcex::Result<()> {
    let client = BackpackClient::public(5_000, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("ping", &[]),
            Case::new("get_time", &[]),
            Case::new("get_markets", &[]),
            Case::new("get_market", &[("product_symbol", BTC_USDC_SPOT)]),
            Case::new(
                "get_order_book_depth",
                &[("product_symbol", BTC_USDC_SPOT), ("limit", "5")],
            ),
            Case::new("get_ticker", &[("product_symbol", BTC_USDC_SPOT)]),
            Case::new("get_open_interest", &[("product_symbol", BTC_USDC_SWAP)]),
            Case::new(
                "get_funding_rates",
                &[("product_symbol", BTC_USDC_SWAP), ("limit", "10")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_funding_rates => get_funding_rates_with,
                        get_market => get_market_with,
                        get_markets => get_markets_with,
                        get_open_interest => get_open_interest_with,
                        get_order_book_depth => get_order_book_depth_with,
                        get_ticker => get_ticker_with,
                        get_time => get_time_with,
                        ping => ping_with,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn backpack_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BACKPACK_API_KEY", "BACKPACK_API_SECRET"]) else {
        return Ok(());
    };
    let client = BackpackClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BACKPACK_API_KEY", "BACKPACK_API_SECRET"],
        vec![
            Case::new("get_account", &[]),
            Case::new("get_balances", &[]),
            Case::new("get_open_orders", &[("product_symbol", BTC_USDC_SPOT)]),
            Case::new(
                "get_fill_history",
                &[("product_symbol", BTC_USDC_SPOT), ("limit", "10")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [get_account => get_account_with, get_balances => get_balances_with, get_fill_history => get_fill_history_with, get_open_orders => get_open_orders_with]
                )
            }
        },
    )
    .await
}
