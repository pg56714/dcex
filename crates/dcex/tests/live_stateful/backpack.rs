use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::backpack::BackpackClient;

use super::common::{
    assert_success, fetch_trading_details, format_step_decimal, live_test_error,
    minimum_order_quantity, params, parse_positive, post_only_buy_price, require_env,
    require_live_fill, require_live_trading, require_order_id, round_down_to_step,
    round_up_to_step,
};

const BTC_USDC_SPOT: &str = "BTC-USDC-SPOT";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn backpack_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BACKPACK_API_KEY", "BACKPACK_API_SECRET"]) else {
        return Ok(());
    };
    let client = BackpackClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        Duration::from_secs(20),
    )?;

    let open_orders = super::common::exchange_method_request(
        &client,
        "get_open_orders",
        params(&[("product_symbol", BTC_USDC_SPOT)]),
    )
    .await?;
    if open_orders
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_open_orders",
            params(&[("product_symbol", BTC_USDC_SPOT)]),
        )
        .await?;
        assert_success(&cancel);
        let remaining = super::common::exchange_method_request(
            &client,
            "get_open_orders",
            params(&[("product_symbol", BTC_USDC_SPOT)]),
        )
        .await?;
        if remaining
            .data
            .as_array()
            .is_some_and(|orders| !orders.is_empty())
        {
            return Err(live_test_error(
                "Backpack still has open BTC-USDC spot orders after cleanup",
            ));
        }
    }

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_order_book_depth",
        params(&[("product_symbol", BTC_USDC_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Backpack, "backpack", BTC_USDC_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_limit_order",
        params(&[
            ("product_symbol", BTC_USDC_SPOT),
            ("side", "Bid"),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("timeInForce", "GTC"),
            ("postOnly", "true"),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId", "id"])?;
    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[
            ("product_symbol", BTC_USDC_SPOT),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access and real fills"]
async fn backpack_spot_direct_live_fill_and_sell() -> dcex::Result<()> {
    if !require_live_fill() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BACKPACK_API_KEY", "BACKPACK_API_SECRET"]) else {
        return Ok(());
    };
    let client = BackpackClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        Duration::from_secs(20),
    )?;
    let orders = super::common::exchange_method_request(
        &client,
        "get_open_orders",
        params(&[("product_symbol", BTC_USDC_SPOT)]),
    )
    .await?;
    if orders
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        return Err(live_test_error(
            "Backpack fill test requires no open BTC-USDC spot orders",
        ));
    }
    let details = fetch_trading_details(Exchange::Backpack, "backpack", BTC_USDC_SPOT).await?;
    let book = super::common::exchange_method_request(
        &client,
        "get_order_book_depth",
        params(&[("product_symbol", BTC_USDC_SPOT), ("limit", "5")]),
    )
    .await?;
    let ask = backpack_best_ask(&book.data)?;
    let step = parse_positive(&details.size_precision, "size_precision")?;
    let minimum = minimum_order_quantity(&ask.to_string(), &details)?
        .parse::<f64>()
        .map_err(|error| live_test_error(format!("invalid Backpack minimum size: {error}")))?;
    let quantity = round_up_to_step(minimum * 2.0, step);
    if quantity * ask > 25.0 {
        return Err(live_test_error(format!(
            "Backpack minimum fill order exceeds 25 USDC: {}",
            quantity * ask
        )));
    }
    let initial_btc = backpack_spot_balance(&client, "BTC").await?;
    let usdc = backpack_spot_balance(&client, "USDC").await?;
    if usdc < quantity * ask * 1.01 {
        return Err(live_test_error("Backpack fill test has insufficient USDC"));
    }

    let lifecycle_result = async {
        let size = format_step_decimal(quantity, step)?;
        let buy = super::common::exchange_method_request(
            &client,
            "place_market_order",
            params(&[
                ("product_symbol", BTC_USDC_SPOT),
                ("side", "Bid"),
                ("quantity", size.as_str()),
                ("autoLend", "false"),
                ("autoLendRedeem", "true"),
            ]),
        )
        .await?;
        assert_success(&buy);
        let mut acquired = 0.0;
        for _ in 0..20 {
            acquired = backpack_spot_balance(&client, "BTC").await? - initial_btc;
            if acquired > 0.0 {
                break;
            }
            tokio::time::sleep(Duration::from_millis(500)).await;
        }
        if acquired <= 0.0 {
            return Err(live_test_error("Backpack market buy did not acquire BTC"));
        }
        close_backpack_spot_delta(&client, initial_btc, step).await?;
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    let cleanup_result = close_backpack_spot_delta(&client, initial_btc, step).await;
    cleanup_result?;
    lifecycle_result
}

async fn backpack_spot_balance(client: &BackpackClient, asset: &str) -> dcex::Result<f64> {
    let balances =
        super::common::exchange_method_request(client, "get_balances", params(&[])).await?;
    Ok(balances
        .data
        .get(asset)
        .and_then(|balance| balance.get("available"))
        .and_then(|value| match value {
            serde_json::Value::Number(value) => value.as_f64(),
            serde_json::Value::String(value) => value.parse().ok(),
            _ => None,
        })
        .unwrap_or(0.0))
}

fn backpack_best_ask(data: &serde_json::Value) -> dcex::Result<f64> {
    data.get("asks")
        .and_then(|asks| asks.as_array())
        .and_then(|asks| asks.first())
        .and_then(|level| level.as_array())
        .and_then(|level| level.first())
        .and_then(|price| {
            price
                .as_str()
                .and_then(|price| price.parse().ok())
                .or_else(|| price.as_f64())
        })
        .ok_or_else(|| live_test_error("Backpack orderbook has no best ask"))
}

async fn close_backpack_spot_delta(
    client: &BackpackClient,
    initial_btc: f64,
    step: f64,
) -> dcex::Result<()> {
    let delta = backpack_spot_balance(client, "BTC").await? - initial_btc;
    let sellable = round_down_to_step(delta.max(0.0), step);
    if sellable > 0.0 {
        let quantity = format_step_decimal(sellable, step)?;
        let sell = super::common::exchange_method_request(
            client,
            "place_market_order",
            params(&[
                ("product_symbol", BTC_USDC_SPOT),
                ("side", "Ask"),
                ("quantity", quantity.as_str()),
                ("autoLend", "true"),
                ("autoLendRedeem", "true"),
            ]),
        )
        .await?;
        assert_success(&sell);
    }
    for _ in 0..20 {
        if backpack_spot_balance(client, "BTC").await? - initial_btc <= step {
            return Ok(());
        }
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    Err(live_test_error("Backpack BTC remains after market sell"))
}
