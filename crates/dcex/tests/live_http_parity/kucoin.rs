use std::time::Duration;

use dcex::exchanges::kucoin::KucoinClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kucoin_public_live_parity() -> dcex::Result<()> {
    let client = KucoinClient::new(None, None, None, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_spot_instrument_info", &[]),
            Case::new("get_spot_ticker", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_spot_orderbook", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_public_trades",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_kline",
                &[("product_symbol", BTC_USDT_SPOT), ("timeframe", "1m")],
            ),
            Case::new("get_futures_contracts", &[]),
            Case::new("get_futures_contract", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_futures_ticker", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_futures_orderbook",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_futures_contract,
                        get_futures_contracts,
                        get_futures_orderbook,
                        get_futures_ticker,
                        get_spot_instrument_info,
                        get_spot_kline,
                        get_spot_orderbook,
                        get_spot_public_trades,
                        get_spot_ticker,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kucoin_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_PASSPHRASE"])
    else {
        return Ok(());
    };
    let client = KucoinClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_PASSPHRASE"],
        vec![
            Case::new("get_account_balance", &[]),
            Case::new("get_futures_account", &[]),
            Case::new("get_futures_positions", &[]),
            Case::new("get_spot_open_orders", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_futures_order_list",
                &[("product_symbol", BTC_USDT_SWAP), ("status", "active")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_account_balance,
                        get_futures_account,
                        get_futures_order_list,
                        get_futures_positions,
                        get_spot_open_orders,
                    ]
                )
            }
        },
    )
    .await
}
