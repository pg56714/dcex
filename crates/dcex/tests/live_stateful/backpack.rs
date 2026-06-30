use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::backpack::BackpackClient;

use super::common::{
    assert_success, fetch_trading_details, live_test_error, minimum_order_quantity, params,
    post_only_buy_price, require_env, require_live_trading, require_order_id,
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
