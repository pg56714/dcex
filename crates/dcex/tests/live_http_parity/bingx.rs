use std::time::Duration;

use dcex::exchanges::bingx::BingxClient;

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bingx_public_live_parity() -> dcex::Result<()> {
    let client = BingxClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new(
                "get_swap_instrument_info",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_orderbook",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new(
                "get_public_trades",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "2")],
            ),
            Case::new(
                "get_kline",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new("get_ticker", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_open_interest", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_mark_price_kline",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new(
                "get_spot_instrument_info",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_orderbook_v2",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("limit", "5"),
                    ("type_", "step0"),
                ],
            ),
            Case::new(
                "get_spot_public_trades",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_kline",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new(
                "get_spot_kline_v2",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("interval", "1m"),
                    ("limit", "2"),
                ],
            ),
            Case::new("get_spot_ticker", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_spot_book_ticker", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_price_ticker",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_kline => get_kline_with,
                        get_mark_price_kline => get_mark_price_kline_with,
                        get_open_interest => get_open_interest_with,
                        get_orderbook => get_orderbook_with,
                        get_public_trades => get_public_trades_with,
                        get_spot_book_ticker => get_spot_book_ticker_with,
                        get_spot_instrument_info => get_spot_instrument_info_with,
                        get_spot_kline => get_spot_kline_with,
                        get_spot_kline_v2 => get_spot_kline_v2_with,
                        get_spot_orderbook => get_spot_orderbook_with,
                        get_spot_orderbook_v2 => get_spot_orderbook_v2_with,
                        get_spot_price_ticker => get_spot_price_ticker_with,
                        get_spot_public_trades => get_spot_public_trades_with,
                        get_spot_ticker => get_spot_ticker_with,
                        get_swap_instrument_info => get_swap_instrument_info_with,
                        get_ticker => get_ticker_with,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bingx_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BINGX_API_KEY", "BINGX_API_SECRET"]) else {
        return Ok(());
    };
    let client = BingxClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BINGX_API_KEY", "BINGX_API_SECRET"],
        vec![
            Case::new("get_account_balance", &[]),
            Case::new("get_swap_account_balance", &[]),
            Case::new("get_spot_account_balance", &[]),
            Case::new("get_fund_account_balance", &[("asset", "USDT")]),
            Case::new("get_all_account_balance", &[]),
            Case::new("get_account_uid", &[]),
            Case::new(
                "get_transferable_coins",
                &[("fromAccount", "fund"), ("toAccount", "spot")],
            ),
            Case::new(
                "get_asset_transfer_records",
                &[
                    ("fromAccount", "fund"),
                    ("toAccount", "spot"),
                    ("pageSize", "5"),
                ],
            ),
            Case::new("get_open_positions", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_fund_flow", &[("limit", "5")]),
            Case::new("get_open_orders", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_order_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
            ),
            Case::new("get_margin_type", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_leverage", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new("get_position_mode", &[]),
            Case::new("get_spot_open_orders", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_order_history",
                &[("product_symbol", BTC_USDT_SPOT), ("pageSize", "5")],
            ),
            Case::new(
                "get_spot_my_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_commission_rate",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_account_balance => get_account_balance_with,
                        get_account_uid => get_account_uid_with,
                        get_all_account_balance => get_all_account_balance_with,
                        get_asset_transfer_records => get_asset_transfer_records_with,
                        get_fund_account_balance => get_fund_account_balance_with,
                        get_fund_flow => get_fund_flow_with,
                        get_leverage => get_leverage_with,
                        get_margin_type => get_margin_type_with,
                        get_open_orders => get_open_orders_with,
                        get_open_positions => get_open_positions_with,
                        get_order_history => get_order_history_with,
                        get_position_mode => get_position_mode_with,
                        get_spot_account_balance => get_spot_account_balance_with,
                        get_spot_commission_rate => get_spot_commission_rate_with,
                        get_spot_my_trades => get_spot_my_trades_with,
                        get_spot_open_orders => get_spot_open_orders_with,
                        get_spot_order_history => get_spot_order_history_with,
                        get_swap_account_balance => get_swap_account_balance_with,
                        get_transferable_coins => get_transferable_coins_with,
                    ]
                )
            }
        },
    )
    .await
}
