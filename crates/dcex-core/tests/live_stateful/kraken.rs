use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::kraken::KrakenClient;

use super::common::{
    assert_success, fetch_trading_details, minimum_order_quantity, params, post_only_buy_price,
    require_env, require_live_trading, require_order_id, BTC_USDT_SPOT,
};

#[tokio::test]
async fn kraken_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["KRAKEN_SPOT_API_KEY", "KRAKEN_SPOT_API_SECRET"]) else {
        return Ok(());
    };
    let client = KrakenClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        None,
        None,
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_spot_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("count", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Kraken, "kraken", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = client
        .private_request(
            "place_spot_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("volume", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["txid"])?;

    let cancel = client
        .private_request("cancel_spot_order", params(&[("txid", order_id.as_str())]))
        .await?;
    assert_success(&cancel);
    Ok(())
}
