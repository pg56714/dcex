use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::mexc::MexcClient;

use super::common::{
    assert_success, fetch_trading_details, minimum_order_quantity, params, post_only_buy_price,
    require_env, require_live_trading, require_order_id, BTC_USDT_SPOT,
};

#[tokio::test]
async fn mexc_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["MEXC_API_KEY", "MEXC_API_SECRET"]) else {
        return Ok(());
    };
    let client = MexcClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_spot_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Mexc, "mexc", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = client
        .private_request(
            "place_spot_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("quantity", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel = client
        .private_request(
            "cancel_spot_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("orderId", order_id.as_str()),
            ]),
        )
        .await?;
    assert_success(&cancel);
    Ok(())
}
