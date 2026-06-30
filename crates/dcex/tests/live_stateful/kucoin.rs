use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::kucoin::KucoinClient;

use super::common::{
    assert_success, fetch_trading_details, live_test_error, minimum_order_quantity, params,
    post_only_buy_price, require_env, require_live_trading, require_order_id, unique_client_id,
    BTC_USDT_SPOT,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kucoin_spot_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "KUCOIN_API_KEY",
        "KUCOIN_API_SECRET",
        "KUCOIN_API_PASSPHRASE",
    ]) else {
        return Ok(());
    };
    let client = KucoinClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let open_orders = super::common::exchange_method_request(
        &client,
        "get_spot_open_orders",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    if open_orders
        .data
        .get("items")
        .and_then(|v| v.as_array())
        .is_some_and(|items| !items.is_empty())
    {
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_spot_all_orders_by_symbol",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        assert_success(&cancel);
        let remaining = super::common::exchange_method_request(
            &client,
            "get_spot_open_orders",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        if remaining
            .data
            .get("items")
            .and_then(|v| v.as_array())
            .is_some_and(|items| !items.is_empty())
        {
            return Err(live_test_error(
                "KuCoin spot still has open BTC-USDT orders after cleanup",
            ));
        }
    }

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::KuCoin, "kucoin", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let size = minimum_order_quantity(&price, &details)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("size", size.as_str()),
            ("price", price.as_str()),
            ("clientOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel = super::common::exchange_method_request(
        &client,
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
