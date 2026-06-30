use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmex::BitmexClient;
use tokio::time::sleep;

use super::common::{
    assert_success, contains_non_empty_array, fetch_trading_details, minimum_order_quantity,
    params, post_only_buy_price, require_env, require_live_trading, require_order_id,
    unique_client_id, wait_for_flat_position, wait_for_positive_position, XBT_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitmex_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITMEX_API_KEY", "BITMEX_API_SECRET"]) else {
        return Ok(());
    };
    let client = BitmexClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    cleanup_bitmex_state(&client).await?;
    if bitmex_available_margin(&client).await? <= 0.0 {
        return Err(super::common::live_test_error(
            "BitMEX live stateful order has insufficient available margin",
        ));
    }

    let orderbook = client
        .get_orderbook(XBT_USDT_SWAP)
        .param("depth", "10")
        .await?;
    let details = fetch_trading_details(Exchange::BitMEX, "bitmex", XBT_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = super::common::exchange_method_request(
        &client,
        "place_post_only_buy_order",
        params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("price", price.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderID"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[("orderID", order_id.as_str())]),
    )
    .await?;
    assert_success(&cancel);

    let opened = super::common::exchange_method_request(
        &client,
        "place_market_buy_order",
        params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&opened);
    assert!(wait_for_positive_position(|| bitmex_position_abs(&client)).await? > 0.0);

    let closed = super::common::exchange_method_request(
        &client,
        "place_market_sell_order",
        params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
            ("execInst", "ReduceOnly"),
        ]),
    )
    .await?;
    assert_success(&closed);
    sleep(Duration::from_secs(1)).await;
    assert_eq!(
        wait_for_flat_position(|| bitmex_position_abs(&client)).await?,
        0.0
    );
    Ok(())
}

async fn cleanup_bitmex_state(client: &BitmexClient) -> dcex::Result<()> {
    if bitmex_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_all_orders",
            params(&[("product_symbol", XBT_USDT_SWAP)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }

    let qty = bitmex_position_qty(client).await?;
    if qty != 0.0 {
        let method = if qty > 0.0 {
            "place_market_sell_order"
        } else {
            "place_market_buy_order"
        };
        let order_qty = (qty.abs().ceil() as i64).to_string();
        let close = super::common::exchange_method_request(
            client,
            method,
            params(&[
                ("product_symbol", XBT_USDT_SWAP),
                ("orderQty", order_qty.as_str()),
                ("clOrdID", unique_client_id("dcexrs").as_str()),
                ("execInst", "ReduceOnly"),
            ]),
        )
        .await?;
        assert_success(&close);
        sleep(Duration::from_secs(1)).await;
    }

    if bitmex_open_orders(client).await? {
        return Err(super::common::live_test_error(
            "BitMEX still has open XBT-USDT swap orders after cleanup",
        ));
    }
    if wait_for_flat_position(|| bitmex_position_abs(client)).await? != 0.0 {
        return Err(super::common::live_test_error(
            "BitMEX XBT-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn bitmex_open_orders(client: &BitmexClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_order",
        params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("filter", "{\"open\":true}"),
            ("count", "100"),
            ("reverse", "true"),
        ]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn bitmex_position_qty(client: &BitmexClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_positions",
        params(&[("filter", "{\"symbol\":\"XBTUSDT\"}")]),
    )
    .await?;
    Ok(super::common::find_f64(&response.data, &["currentQty"]).unwrap_or(0.0))
}

async fn bitmex_position_abs(client: &BitmexClient) -> dcex::Result<f64> {
    Ok(bitmex_position_qty(client).await?.abs())
}

async fn bitmex_available_margin(client: &BitmexClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_margin",
        params(&[("currency", "USDt")]),
    )
    .await?;
    Ok(super::common::find_f64(&response.data, &["availableMargin"]).unwrap_or(0.0))
}
