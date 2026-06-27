use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::aster::AsterClient;

use super::common::{
    assert_success, fetch_trading_details, minimum_order_quantity, params, post_only_buy_price,
    require_env, require_live_trading, require_order_id, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn aster_futures_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "ASTER_USER_ADDRESS",
        "ASTER_SIGNER_ADDRESS",
        "ASTER_PRIVATE_KEY",
    ]) else {
        return Ok(());
    };
    let client = AsterClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let open_orders = super::common::exchange_method_request(
        &client,
        "get_futures_open_orders",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    if open_orders
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        eprintln!("skipping Aster futures live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }

    let orderbook = client.get_futures_orderbook(BTC_USDT_SWAP).limit(5).await?;
    let details = fetch_trading_details(Exchange::Aster, "aster", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_futures_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("timeInForce", "GTC"),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_futures_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}
