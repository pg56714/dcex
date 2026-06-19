use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::bitmex::BitmexClient;

use super::common::{require_env, run_cases, run_private_cases, Case};

const XBT_USDT_SWAP: &str = "XBT-USDT-SWAP";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitmex_public_live_parity() -> dcex::Result<()> {
    let client = BitmexClient::new(None, None, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_instrument_info", &[]),
            Case::new("get_instrument_info", &[("product_symbol", XBT_USDT_SWAP)]),
            Case::new(
                "get_orderbook",
                &[("product_symbol", XBT_USDT_SWAP), ("depth", "10")],
            ),
            Case::new(
                "get_trades",
                &[("product_symbol", XBT_USDT_SWAP), ("count", "2")],
            ),
            Case::new(
                "get_ticker",
                &[("symbol", XBT_USDT_SWAP), ("binSize", "1m"), ("count", "2")],
            ),
            Case::new(
                "get_kline",
                &[("symbol", XBT_USDT_SWAP), ("binSize", "1m"), ("count", "2")],
            ),
            Case::new(
                "get_funding",
                &[("product_symbol", XBT_USDT_SWAP), ("count", "2")],
            ),
            Case::new(
                "get_liquidations",
                &[("product_symbol", XBT_USDT_SWAP), ("count", "2")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { bitmex_public_case(&client, case).await }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitmex_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BITMEX_API_KEY", "BITMEX_API_SECRET"]) else {
        return Ok(());
    };
    let client = BitmexClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BITMEX_API_KEY", "BITMEX_API_SECRET"],
        vec![
            Case::new("get_wallet_summary", &[("currency", "all")]),
            Case::new("get_positions", &[]),
            Case::new("get_margining_mode", &[]),
            Case::new("get_margin", &[("currency", "all")]),
            Case::new(
                "get_order",
                &[
                    ("product_symbol", XBT_USDT_SWAP),
                    ("filter", r#"{"open":true}"#),
                    ("count", "10"),
                    ("reverse", "true"),
                ],
            ),
            Case::new(
                "get_executions",
                &[("product_symbol", XBT_USDT_SWAP), ("count", "5")],
            ),
            Case::new(
                "get_trade_history",
                &[("product_symbol", XBT_USDT_SWAP), ("count", "5")],
            ),
            Case::new("get_trading_volume", &[]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_executions,
                        get_margin,
                        get_margining_mode,
                        get_order,
                        get_positions,
                        get_trade_history,
                        get_trading_volume,
                        get_wallet_summary,
                    ]
                )
            }
        },
    )
    .await
}

async fn bitmex_public_case(client: &BitmexClient, case: Case) -> dcex::Result<ValidatedResponse> {
    let params = Params(case.params);
    match case.method {
        "get_instrument_info" => {
            client
                .get_instrument_info(
                    params.get("product_symbol"),
                    params.get("filter"),
                    params.get("count"),
                )
                .await
        }
        "get_orderbook" => {
            client
                .get_orderbook(params.required("product_symbol")?, params.get("depth"))
                .await
        }
        "get_trades" => client.get_trades(params.into_inner()).await,
        "get_ticker" => client.get_ticker(params.into_inner()).await,
        "get_kline" => client.get_kline(params.into_inner()).await,
        "get_funding" => client.get_funding(params.into_inner()).await,
        "get_liquidations" => client.get_liquidations(params.into_inner()).await,
        method => Err(dcex::DcexError::InvalidInput(format!(
            "unsupported BitMEX public test method: {method}",
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

    fn into_inner(self) -> Vec<(String, String)> {
        self.0
    }
}
