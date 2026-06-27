use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::binance::BinanceClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn binance_public_live_parity() -> dcex::Result<()> {
    let client = BinanceClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new(
                "get_spot_exchange_info",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new("get_server_time", &[("market_type", "spot")]),
            Case::new("get_server_time", &[("market_type", "swap")]),
            Case::new("get_futures_exchange_info", &[]),
            Case::new("get_futures_ticker", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_klines",
                &[("product_symbol", BTC_USDT_SWAP), ("interval", "1m")],
            ),
            Case::new(
                "get_futures_premium_index",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_funding_rate",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_open_interest",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_open_interest_history",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_global_long_short_account_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_top_long_short_account_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_top_long_short_position_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_taker_buy_sell_volume",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_basis",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("contractType", "PERPETUAL"),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { binance_public_case(&client, case).await }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn binance_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BINANCE_API_KEY", "BINANCE_API_SECRET"]) else {
        return Ok(());
    };
    let client = BinanceClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BINANCE_API_KEY", "BINANCE_API_SECRET"],
        vec![
            Case::new("get_account_balance", &[("market_type", "spot")]),
            Case::new("get_account_balance", &[("market_type", "swap")]),
            Case::new("get_futures_account_info", &[]),
            Case::new("get_wallet_balance", &[("quoteAsset", "USDT")]),
            Case::new(
                "get_funding_wallet",
                &[("asset", "USDT"), ("needBtcValuation", "true")],
            ),
            Case::new(
                "get_universal_transfer_history",
                &[("type", "FUNDING_MAIN"), ("size", "1")],
            ),
            Case::new("get_income_history", &[]),
        ],
        |case| {
            let client = client.clone();
            async move { binance_private_case(&client, case).await }
        },
    )
    .await
}

async fn binance_public_case(
    client: &BinanceClient,
    case: Case,
) -> dcex::Result<ValidatedResponse> {
    client.public_request(case.method, case.params).await
}

async fn binance_private_case(
    client: &BinanceClient,
    case: Case,
) -> dcex::Result<ValidatedResponse> {
    client.private_request(case.method, case.params).await
}
