use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::kraken::KrakenClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    assert_success, contains_non_empty_array, fetch_trading_details, find_f64, first_bid_price,
    format_transfer_amount_ceil, minimum_order_quantity, params, post_only_buy_price, require_env,
    require_live_trading, require_order_id, sum_abs_values_for_symbols, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USD_SWAP,
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

#[tokio::test]
async fn kraken_futures_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["KRAKEN_FUTURES_API_KEY", "KRAKEN_FUTURES_API_SECRET"]) else {
        return Ok(());
    };
    let client = KrakenClient::new(
        None,
        None,
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if kraken_futures_open_orders(&client).await? {
        eprintln!("skipping Kraken futures live stateful order; open BTC-USD swap orders exist");
        return Ok(());
    }
    if kraken_futures_position_abs(&client).await? > 0.0 {
        eprintln!("skipping Kraken futures live stateful order; BTC-USD swap position exists");
        return Ok(());
    }

    let orderbook = client
        .public_request(
            "get_futures_orderbook",
            params(&[("product_symbol", BTC_USD_SWAP)]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Kraken, "kraken", BTC_USD_SWAP).await?;
    let price = kraken_futures_post_only_buy_price(&orderbook.data)?;
    let quantity = kraken_futures_quantity(&details);
    let transferred = match ensure_kraken_futures_margin(&client, 0.5).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order = client
        .private_request(
            "place_futures_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USD_SWAP),
                ("size", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id"])?;

    let cancel = client
        .private_request(
            "cancel_futures_order",
            params(&[("order_id", order_id.as_str())]),
        )
        .await?;
    assert_success(&cancel);

    let opened = client
        .private_request(
            "place_futures_market_buy_order",
            params(&[
                ("product_symbol", BTC_USD_SWAP),
                ("size", quantity.as_str()),
            ]),
        )
        .await?;
    assert_success(&opened);
    assert!(wait_for_positive_position(|| kraken_futures_position_abs(&client)).await? > 0.0);

    let closed = client
        .private_request(
            "place_futures_market_sell_order",
            params(&[
                ("product_symbol", BTC_USD_SWAP),
                ("size", quantity.as_str()),
                ("reduceOnly", "true"),
            ]),
        )
        .await?;
    assert_success(&closed);
    assert_eq!(
        wait_for_flat_position(|| kraken_futures_position_abs(&client)).await?,
        0.0
    );
    return_kraken_futures_margin(&client, transferred).await?;
    Ok(())
}

async fn kraken_futures_open_orders(client: &KrakenClient) -> dcex::Result<bool> {
    let response = client
        .private_request("get_futures_open_orders", Vec::new())
        .await?;
    Ok(contains_non_empty_array(&response.data, &["openOrders"]))
}

async fn kraken_futures_position_abs(client: &KrakenClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_futures_open_positions", Vec::new())
        .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["PF_XBTUSD"],
        &["size", "qty", "quantity"],
    ))
}

async fn ensure_kraken_futures_margin(
    client: &KrakenClient,
    required: f64,
) -> dcex::Result<Option<f64>> {
    let accounts = client
        .private_request("get_futures_accounts", Vec::new())
        .await?;
    let flex = kraken_flex_available(&accounts.data);
    if flex >= required {
        return Ok(Some(0.0));
    }
    let needed = required - flex;
    if kraken_cash_available(&accounts.data, "usdt") < needed {
        eprintln!("skipping Kraken futures live stateful order; insufficient cash USDT");
        return Ok(None);
    }
    let amount = format_transfer_amount_ceil(needed, 8);
    let response = client
        .private_request(
            "futures_wallet_transfer",
            params(&[
                ("amount", amount.as_str()),
                ("fromAccount", "cash"),
                ("toAccount", "flex"),
                ("unit", "USDT"),
            ]),
        )
        .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_kraken_futures_margin(client: &KrakenClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let accounts = client
        .private_request("get_futures_accounts", Vec::new())
        .await?;
    let amount = amount.min(kraken_flex_available(&accounts.data));
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_ceil(amount, 8);
    let response = client
        .private_request(
            "futures_wallet_transfer",
            params(&[
                ("amount", amount.as_str()),
                ("fromAccount", "flex"),
                ("toAccount", "cash"),
                ("unit", "USDT"),
            ]),
        )
        .await?;
    assert_success(&response);
    Ok(())
}

fn kraken_flex_available(data: &Value) -> f64 {
    data.get("accounts")
        .and_then(|accounts| accounts.get("flex"))
        .and_then(|flex| find_f64(flex, &["availableMargin"]))
        .unwrap_or(0.0)
}

fn kraken_cash_available(data: &Value, unit: &str) -> f64 {
    data.get("accounts")
        .and_then(|accounts| accounts.get("cash"))
        .and_then(|cash| cash.get("balances"))
        .and_then(|balances| balances.get(unit))
        .and_then(|balance| find_f64(balance, &["available", "balance", "amount"]))
        .unwrap_or(0.0)
}

fn kraken_futures_post_only_buy_price(data: &Value) -> dcex::Result<String> {
    let bid = first_bid_price(data)?;
    let tick = 0.5;
    let price = ((bid * 0.5) / tick).floor() * tick;
    if price <= 0.0 {
        return Err(dcex::DcexError::Decode(format!(
            "Kraken futures orderbook produced invalid bid price: {data}"
        )));
    }
    Ok(format!("{price:.1}"))
}

fn kraken_futures_quantity(details: &dcex::product_table::TradingDetails) -> String {
    let min_size = details
        .min_size
        .parse::<f64>()
        .unwrap_or(0.0001)
        .max(0.0001);
    format!("{min_size:.4}")
}
