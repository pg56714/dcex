use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::aster::AsterClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn aster_public_live_parity() -> dcex::Result<()> {
    let client = AsterClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("ping_spot", &[]),
            Case::new("ping_futures", &[]),
            Case::new("get_spot_server_time", &[]),
            Case::new("get_futures_server_time", &[]),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_futures_orderbook",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new(
                "get_futures_ticker_24hr",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { aster_public_case(&client, case).await }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn aster_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&[
        "ASTER_USER_ADDRESS",
        "ASTER_SIGNER_ADDRESS",
        "ASTER_PRIVATE_KEY",
    ]) else {
        return Ok(());
    };
    let client = AsterClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &[
            "ASTER_USER_ADDRESS",
            "ASTER_SIGNER_ADDRESS",
            "ASTER_PRIVATE_KEY",
        ],
        vec![
            Case::new("get_spot_account", &[]),
            Case::new("get_futures_balance", &[]),
            Case::new("get_futures_account", &[]),
            Case::new(
                "get_futures_position_risk",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { client.private_request(case.method, case.params).await }
        },
    )
    .await
}

async fn aster_public_case(client: &AsterClient, case: Case) -> dcex::Result<ValidatedResponse> {
    client.public_request(case.method, case.params).await
}
