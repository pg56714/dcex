use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmex::BitmexClient;

use super::common::{
    assert_success, fetch_trading_details, minimum_order_quantity, params, post_only_buy_price,
    require_env, require_live_trading, require_order_id, XBT_USDT_SWAP,
};

#[tokio::test]
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

    let orderbook = client
        .public_request(
            "get_orderbook",
            params(&[("product_symbol", XBT_USDT_SWAP), ("depth", "10")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::BitMEX, "bitmex", XBT_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = client
        .private_request(
            "place_post_only_buy_order",
            params(&[
                ("product_symbol", XBT_USDT_SWAP),
                ("orderQty", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderID"])?;

    let cancel = client
        .private_request("cancel_order", params(&[("orderID", order_id.as_str())]))
        .await?;
    assert_success(&cancel);
    Ok(())
}
