use std::time::Duration;

use dcex::exchanges::kraken::KrakenClient;

use super::common::{require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USD_SWAP};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kraken_public_live_parity() -> dcex::Result<()> {
    let client = KrakenClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_server_time", &[]),
            Case::new("get_spot_asset_pairs", &[("pair", "XBTUSDT")]),
            Case::new("get_spot_ticker", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("count", "5")],
            ),
            Case::new(
                "get_spot_public_trades",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_kline",
                &[("product_symbol", BTC_USDT_SPOT), ("interval", "1")],
            ),
            Case::new(
                "get_futures_instruments",
                &[("contractType", "flexible_futures")],
            ),
            Case::new("get_futures_tickers", &[("product_symbol", BTC_USD_SWAP)]),
            Case::new("get_futures_orderbook", &[("product_symbol", BTC_USD_SWAP)]),
            Case::new(
                "get_futures_public_trades",
                &[("product_symbol", BTC_USD_SWAP)],
            ),
            Case::new(
                "get_futures_kline",
                &[
                    ("product_symbol", BTC_USD_SWAP),
                    ("timeframe", "1m"),
                    ("count", "5"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_futures_instruments => get_futures_instruments_with,
                        get_futures_kline => get_futures_kline_with,
                        get_futures_orderbook => get_futures_orderbook_with,
                        get_futures_public_trades => get_futures_public_trades_with,
                        get_futures_tickers => get_futures_tickers_with,
                        get_server_time => get_server_time_with,
                        get_spot_asset_pairs => get_spot_asset_pairs_with,
                        get_spot_kline => get_spot_kline_with,
                        get_spot_orderbook => get_spot_orderbook_with,
                        get_spot_public_trades => get_spot_public_trades_with,
                        get_spot_ticker => get_spot_ticker_with,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kraken_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&[
        "KRAKEN_SPOT_API_KEY",
        "KRAKEN_SPOT_API_SECRET",
        "KRAKEN_FUTURES_API_KEY",
        "KRAKEN_FUTURES_API_SECRET",
    ]) else {
        return Ok(());
    };
    let client = KrakenClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Some(keys[3].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &[
            "KRAKEN_SPOT_API_KEY",
            "KRAKEN_SPOT_API_SECRET",
            "KRAKEN_FUTURES_API_KEY",
            "KRAKEN_FUTURES_API_SECRET",
        ],
        vec![
            Case::new("get_spot_account_balance", &[]),
            Case::new("get_spot_trade_balance", &[("asset", "USDT")]),
            Case::new("get_spot_open_positions", &[]),
            Case::new(
                "get_spot_ledgers",
                &[("asset", "USDT"), ("without_count", "true")],
            ),
            Case::new(
                "get_spot_trade_volume",
                &[("pair", "XBTUSDT"), ("fee_info", "true")],
            ),
            Case::new("get_spot_open_orders", &[]),
            Case::new("get_spot_closed_orders", &[]),
            Case::new("get_spot_trade_history", &[]),
            Case::new("get_futures_accounts", &[]),
            Case::new("get_futures_open_positions", &[]),
            Case::new("get_futures_fills", &[]),
            Case::new("get_futures_open_orders", &[]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_futures_accounts => get_futures_accounts_with,
                        get_futures_fills => get_futures_fills_with,
                        get_futures_open_orders => get_futures_open_orders_with,
                        get_futures_open_positions => get_futures_open_positions_with,
                        get_spot_account_balance => get_spot_account_balance_with,
                        get_spot_closed_orders => get_spot_closed_orders_with,
                        get_spot_ledgers => get_spot_ledgers_with,
                        get_spot_open_orders => get_spot_open_orders_with,
                        get_spot_open_positions => get_spot_open_positions_with,
                        get_spot_trade_balance => get_spot_trade_balance_with,
                        get_spot_trade_history => get_spot_trade_history_with,
                        get_spot_trade_volume => get_spot_trade_volume_with,
                    ]
                )
            }
        },
    )
    .await
}
