use std::time::Duration;

use dcex::exchanges::okx::OkxClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn okx_public_live_parity() -> dcex::Result<()> {
    let client = OkxClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_public_instruments", &[("instType", "SPOT")]),
            Case::new("get_funding_rate", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_funding_rate_history",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_open_interest", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_position_tiers",
                &[
                    ("instType", "SWAP"),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("tdMode", "cross"),
                ],
            ),
            Case::new("get_trading_data_support_coin", &[]),
            Case::new("get_taker_volume", &[("ccy", "BTC"), ("instType", "SPOT")]),
            Case::new(
                "get_contract_taker_volume",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_long_short_ratio", &[("ccy", "BTC")]),
            Case::new(
                "get_contract_long_short_ratio",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_top_trader_long_short_account_ratio",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_top_trader_long_short_position_ratio",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_contracts_open_interest_and_volume", &[("ccy", "BTC")]),
            Case::new(
                "get_contract_open_interest_history",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_candles_ticks", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_orderbook", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_tickers", &[("instType", "SPOT")]),
            Case::new("get_public_trades", &[("product_symbol", BTC_USDT_SPOT)]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_candles_ticks,
                        get_contract_long_short_ratio,
                        get_contract_open_interest_history,
                        get_contract_taker_volume,
                        get_contracts_open_interest_and_volume,
                        get_funding_rate,
                        get_funding_rate_history,
                        get_long_short_ratio,
                        get_open_interest,
                        get_orderbook,
                        get_position_tiers,
                        get_public_instruments,
                        get_public_trades,
                        get_taker_volume,
                        get_tickers,
                        get_top_trader_long_short_account_ratio,
                        get_top_trader_long_short_position_ratio,
                        get_trading_data_support_coin,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn okx_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"]) else {
        return Ok(());
    };
    let client = OkxClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        "0".to_string(),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"],
        vec![
            Case::new(
                "get_account_instruments",
                &[("instType", "SPOT"), ("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new("get_account_balance", &[]),
            Case::new("get_positions", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_positions_history",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new("get_position_risk", &[]),
            Case::new("get_account_bills", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_account_bills_archive",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new("get_account_config", &[]),
            Case::new(
                "get_max_order_size",
                &[("product_symbol", BTC_USDT_SPOT), ("tdMode", "isolated")],
            ),
            Case::new(
                "get_max_avail_size",
                &[("product_symbol", BTC_USDT_SPOT), ("tdMode", "cash")],
            ),
            Case::new(
                "get_leverage",
                &[("product_symbol", BTC_USDT_SWAP), ("mgnMode", "cross")],
            ),
            Case::new(
                "get_adjust_leverage",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("instType", "SWAP"),
                    ("mgnMode", "cross"),
                    ("lever", "3"),
                ],
            ),
            Case::new(
                "get_max_loan",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("mgnMode", "cross"),
                    ("mgnCcy", "USDT"),
                ],
            ),
            Case::new("get_spot_fee_rates", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_interest_accrued", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_interest_rate", &[]),
            Case::new("get_max_withdrawal", &[]),
            Case::new("get_interest_limits", &[]),
            Case::new("get_currencies", &[]),
            Case::new("get_balances", &[]),
            Case::new("get_asset_valuation", &[]),
            Case::new("get_bills", &[]),
            Case::new("get_deposit_address", &[("ccy", "BTC")]),
            Case::new("get_deposit_history", &[]),
            Case::new("get_exchange_list", &[]),
            Case::new("get_convert_currencies", &[]),
            Case::new("get_convert_history", &[]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_account_balance,
                        get_account_bills,
                        get_account_bills_archive,
                        get_account_config,
                        get_account_instruments,
                        get_adjust_leverage,
                        get_asset_valuation,
                        get_balances,
                        get_bills,
                        get_convert_currencies,
                        get_convert_history,
                        get_currencies,
                        get_deposit_address,
                        get_deposit_history,
                        get_exchange_list,
                        get_spot_fee_rates,
                        get_interest_accrued,
                        get_interest_limits,
                        get_interest_rate,
                        get_leverage,
                        get_max_avail_size,
                        get_max_loan,
                        get_max_order_size,
                        get_max_withdrawal,
                        get_position_risk,
                        get_positions,
                        get_positions_history,
                    ]
                )
            }
        },
    )
    .await
}
