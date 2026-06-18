use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmart::BitmartClient;

use super::common::{
    account_restriction, assert_success, fetch_trading_details, find_f64,
    minimum_order_quantity_with_step, params, price_below_market, require_env,
    require_live_trading, require_order_id, DOGE_USDT_SPOT,
};

#[tokio::test]
async fn bitmart_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"]) else {
        return Ok(());
    };
    let client = BitmartClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let ticker = client
        .public_request(
            "get_ticker_of_a_pair",
            params(&[("product_symbol", DOGE_USDT_SPOT)]),
        )
        .await?;
    let bid = find_f64(
        &ticker.data,
        &["bid_px", "bidPrice", "last", "last_price", "lastPrice"],
    )
    .ok_or_else(|| {
        dcex::DcexError::Decode(format!(
            "BitMart ticker response has no usable bid/last price: {ticker:?}"
        ))
    })?;
    let details = fetch_trading_details(Exchange::BitMart, "bitmart", DOGE_USDT_SPOT).await?;
    let price = price_below_market(bid, &details, 0.95)?;
    let size = minimum_order_quantity_with_step(&price, &details, Some(&details.min_size))?;

    let order = match client
        .private_request(
            "place_spot_post_only_limit_buy_order",
            params(&[
                ("product_symbol", DOGE_USDT_SPOT),
                ("size", size.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await
    {
        Ok(response) => response,
        Err(error)
            if account_restriction(&error, &["33136", "60052", "personal verification", "kyc"]) =>
        {
            eprintln!("skipping BitMart stateful order due account restriction: {error}");
            return Ok(());
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id", "orderId"])?;

    let cancel = client
        .private_request(
            "cancel_spot_order",
            params(&[
                ("product_symbol", DOGE_USDT_SPOT),
                ("order_id", order_id.as_str()),
            ]),
        )
        .await?;
    assert_success(&cancel);
    Ok(())
}
