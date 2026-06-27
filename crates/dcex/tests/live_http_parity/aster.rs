use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::aster::{AsterClient, AsterLimitParams, AsterOptionalSymbolParams};

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
    let params = Params(case.params);
    match case.method {
        "ping_spot" => client.ping_spot().await,
        "ping_futures" => client.ping_futures().await,
        "get_spot_server_time" => client.get_spot_server_time().await,
        "get_futures_server_time" => client.get_futures_server_time().await,
        "get_spot_orderbook" => {
            client
                .get_spot_orderbook_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
        }
        "get_futures_orderbook" => {
            client
                .get_futures_orderbook_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
        }
        "get_futures_ticker_24hr" => {
            client
                .get_futures_ticker_24hr_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
        }
        method => Err(dcex::DcexError::InvalidInput(format!(
            "unsupported Aster public test method: {method}",
        ))),
    }
}

struct Params(Vec<(String, String)>);

impl Params {
    fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    fn required(&self, key: &str) -> dcex::Result<&str> {
        self.get(key)
            .ok_or_else(|| dcex::DcexError::InvalidInput(format!("missing {key}")))
    }

    fn u64(&self, key: &str) -> dcex::Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    dcex::DcexError::InvalidInput(format!("invalid {key}: {error}"))
                })
            })
            .transpose()
    }
}
