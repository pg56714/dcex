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
                        get_adl_alert => get_adl_alert_with,
                        get_delivery_price => get_delivery_price_with,
                        get_funding_rate_history => get_funding_rate_history_with,
                        get_historical_volatility => get_historical_volatility_with,
                        get_instruments_info => get_instruments_info_with,
                        get_insurance_pool => get_insurance_pool_with,
                        get_kline => get_kline_with,
                        get_long_short_ratio => get_long_short_ratio_with,
                        get_open_interest => get_open_interest_with,
                        get_order_price_limit => get_order_price_limit_with,
                        get_orderbook => get_orderbook_with,
                        get_public_trade_history => get_public_trade_history_with,
                        get_risk_limit => get_risk_limit_with,
                        get_tickers => get_tickers_with,
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
                        get_account_info => get_account_info_with,
                        get_borrow_history => get_borrow_history_with,
                        get_coin_balance => get_coin_balance_with,
                        get_coin_info => get_coin_info_with,
                        get_coins_balance => get_coins_balance_with,
                        get_closed_pnl => get_closed_pnl_with,
                        get_collateral_info => get_collateral_info_with,
                        get_deposit_records => get_deposit_records_with,
                        get_fee_rates => get_fee_rates_with,
                        get_internal_deposit_records => get_internal_deposit_records_with,
                        get_internal_transfer_records => get_internal_transfer_records_with,
                        get_master_deposit_address => get_master_deposit_address_with,
                        get_positions => get_positions_with,
                        get_spot_asset_info => get_spot_asset_info_with,
                        get_sub_uid => get_sub_uid_with,
                        get_transaction_log => get_transaction_log_with,
                        get_transferable_amount => get_transferable_amount_with,
                        get_transferable_coin => get_transferable_coin_with,
                        get_universal_transfer_records => get_universal_transfer_records_with,
                        get_wallet_balance => get_wallet_balance_with,
                        get_withdrawable_amount => get_withdrawable_amount_with,
                    ]
                )
            }
        },
    )
    .await
}
