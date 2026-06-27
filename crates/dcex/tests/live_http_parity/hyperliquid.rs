use std::time::Duration;

use dcex::exchanges::hyperliquid::HyperliquidClient;

use super::common::{require_env, run_cases, run_private_cases, Case, BTC_USD_SWAP};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn hyperliquid_public_live_parity() -> dcex::Result<()> {
    let client = HyperliquidClient::public(false, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_meta", &[]),
            Case::new("get_spot_meta", &[]),
            Case::new("get_meta_and_asset_ctxs", &[]),
            Case::new("get_l2book", &[("product_symbol", BTC_USD_SWAP)]),
            Case::new(
                "get_funding_rate_history",
                &[("product_symbol", BTC_USD_SWAP), ("startTime", "1")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_funding_rate_history => get_funding_rate_history_with,
                        get_l2book => get_l2book_with,
                        get_meta => get_meta_with,
                        get_meta_and_asset_ctxs => get_meta_and_asset_ctxs_with,
                        get_spot_meta => get_spot_meta_with,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn hyperliquid_account_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["HYPERLIQUID_WALLET_ADDRESS"]) else {
        return Ok(());
    };
    let client =
        HyperliquidClient::for_wallet_address(false, keys[0].clone(), Duration::from_secs(20))?;
    run_private_cases(
        &["HYPERLIQUID_WALLET_ADDRESS"],
        vec![
            Case::new("open_orders", &[("user", keys[0].as_str())]),
            Case::new("user_fills", &[("user", keys[0].as_str())]),
            Case::new("portfolio", &[("user", keys[0].as_str())]),
        ],
        |case| {
            let client = client.clone();
            async move { client.public_request(case.method, case.params).await }
        },
    )
    .await
}
