use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmex::{BitmexClient, BitmexOrderbookParams};
use tokio::time::sleep;

use super::common::{
    assert_success, contains_non_empty_array, fetch_trading_details, minimum_order_quantity,
    params, post_only_buy_price, require_env, require_live_trading, require_order_id,
    sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_positive_position, XBT_USDT_SWAP,
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
    if bitmex_open_orders(&client).await? {
        eprintln!("skipping BitMEX live stateful order; open XBT-USDT swap orders exist");
        return Ok(());
    }
    if bitmex_position_abs(&client).await? > 0.0 {
        eprintln!("skipping BitMEX live stateful order; XBT-USDT swap position exists");
        return Ok(());
    }
    if bitmex_available_margin(&client).await? <= 0.0 {
        eprintln!("skipping BitMEX live stateful order; insufficient available margin");
        return Ok(());
    }

    let orderbook = client
        .get_orderbook_with(XBT_USDT_SWAP, BitmexOrderbookParams { depth: Some("10") })
        .await?;
    let details = fetch_trading_details(Exchange::BitMEX, "bitmex", XBT_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = client
        .place_post_only_buy_order_with(params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("price", price.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderID"])?;

    let cancel = client
        .cancel_order_with(params(&[("orderID", order_id.as_str())]))
        .await?;
    assert_success(&cancel);

    let opened = client
        .place_market_buy_order_with(params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&opened);
    assert!(wait_for_positive_position(|| bitmex_position_abs(&client)).await? > 0.0);

    let closed = client
        .place_market_sell_order_with(params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("orderQty", quantity.as_str()),
            ("clOrdID", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&closed);
    sleep(Duration::from_secs(1)).await;
    assert_eq!(
        wait_for_flat_position(|| bitmex_position_abs(&client)).await?,
        0.0
    );
    Ok(())
}

async fn bitmex_open_orders(client: &BitmexClient) -> dcex::Result<bool> {
    let response = client
        .get_order_with(params(&[
            ("product_symbol", XBT_USDT_SWAP),
            ("filter", "{\"open\":true}"),
            ("count", "100"),
            ("reverse", "true"),
        ]))
        .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn bitmex_position_abs(client: &BitmexClient) -> dcex::Result<f64> {
    let response = client
        .get_positions_with(params(&[("filter", "{\"symbol\":\"XBTUSDT\"}")]))
        .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["XBTUSDT"],
        &["currentQty"],
    ))
}

async fn bitmex_available_margin(client: &BitmexClient) -> dcex::Result<f64> {
    let response = client
        .get_margin_with(params(&[("currency", "USDt")]))
        .await?;
    Ok(super::common::find_f64(&response.data, &["availableMargin"]).unwrap_or(0.0))
}
