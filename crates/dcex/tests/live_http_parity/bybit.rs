use std::time::Duration;

use dcex::exchanges::bybit::BybitClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bybit_public_live_parity() -> dcex::Result<()> {
    let client = BybitClient::public(5_000, true, Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_instruments_info", &[("category", "spot")]),
            Case::new(
                "get_kline",
                &[("product_symbol", BTC_USDT_SPOT), ("interval", "1m")],
            ),
            Case::new("get_orderbook", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_tickers", &[("category", "linear")]),
            Case::new(
                "get_funding_rate_history",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_public_trade_history",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "10")],
            ),
            Case::new(
                "get_open_interest",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("intervalTime", "5min"),
                    ("limit", "10"),
                ],
            ),
            Case::new(
                "get_long_short_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5min"),
                    ("limit", "10"),
                ],
            ),
            Case::new(
                "get_historical_volatility",
                &[("category", "option"), ("baseCoin", "BTC"), ("period", "7")],
            ),
            Case::new("get_insurance_pool", &[("coin", "USDT")]),
            Case::new(
                "get_delivery_price",
                &[("category", "linear"), ("baseCoin", "BTC"), ("limit", "10")],
            ),
            Case::new(
                "get_order_price_limit",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_adl_alert", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_risk_limit",
                &[("category", "linear"), ("product_symbol", BTC_USDT_SWAP)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_adl_alert,
                        get_delivery_price,
                        get_funding_rate_history,
                        get_historical_volatility,
                        get_instruments_info,
                        get_insurance_pool,
                        get_kline,
                        get_long_short_ratio,
                        get_open_interest,
                        get_order_price_limit,
                        get_orderbook,
                        get_public_trade_history,
                        get_risk_limit,
                        get_tickers,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bybit_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BYBIT_API_KEY", "BYBIT_API_SECRET"]) else {
        return Ok(());
    };
    let client = BybitClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        true,
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BYBIT_API_KEY", "BYBIT_API_SECRET"],
        vec![
            Case::new("get_wallet_balance", &[]),
            Case::new("get_transferable_amount", &[("coins", "BTC,ETH")]),
            Case::new("get_borrow_history", &[]),
            Case::new("get_collateral_info", &[]),
            Case::new("get_fee_rates", &[]),
            Case::new("get_account_info", &[]),
            Case::new("get_transaction_log", &[]),
            Case::new("get_coin_info", &[]),
            Case::new("get_sub_uid", &[]),
            Case::new("get_spot_asset_info", &[]),
            Case::new("get_coins_balance", &[("accountType", "FUND")]),
            Case::new(
                "get_coin_balance",
                &[("accountType", "FUND"), ("coin", "BTC")],
            ),
            Case::new("get_withdrawable_amount", &[("coin", "USDT")]),
            Case::new("get_internal_transfer_records", &[]),
            Case::new(
                "get_transferable_coin",
                &[("fromAccountType", "FUND"), ("toAccountType", "UNIFIED")],
            ),
            Case::new("get_universal_transfer_records", &[]),
            Case::new("get_deposit_records", &[]),
            Case::new("get_internal_deposit_records", &[]),
            Case::new("get_master_deposit_address", &[("coin", "USDT")]),
            Case::new("get_positions", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_closed_pnl", &[]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_account_info,
                        get_borrow_history,
                        get_coin_balance,
                        get_coin_info,
                        get_coins_balance,
                        get_closed_pnl,
                        get_collateral_info,
                        get_deposit_records,
                        get_fee_rates,
                        get_internal_deposit_records,
                        get_internal_transfer_records,
                        get_master_deposit_address,
                        get_positions,
                        get_spot_asset_info,
                        get_sub_uid,
                        get_transaction_log,
                        get_transferable_amount,
                        get_transferable_coin,
                        get_universal_transfer_records,
                        get_wallet_balance,
                        get_withdrawable_amount,
                    ]
                )
            }
        },
    )
    .await
}
