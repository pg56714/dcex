use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::ondo::OndoClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    live_test_error, params, require_env, require_live_fill, require_live_trading, unique_client_id,
};

const MARKET: &str = "BTC-USD.P";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn ondo_direct_live_post_only_order_and_cancel() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["ONDO_API_KEY_ID", "ONDO_API_SECRET"]) else {
        return Ok(());
    };
    let client = OndoClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    require_ondo_clean_account(&client).await?;
    let (size, price) = ondo_order_amounts(&client, false).await?;
    let client_id = unique_client_id("dcex-rs-");
    let mut order_id = None;
    let lifecycle_result = async {
        let placed = super::common::exchange_method_request(
            &client,
            "place_order",
            params(&[
                ("market", MARKET),
                ("side", "buy"),
                ("type", "limit"),
                ("price", price.as_str()),
                ("size", size.as_str()),
                ("timeInForce", "GTC"),
                ("postOnly", "true"),
                ("clientOrderId", client_id.as_str()),
            ]),
        )
        .await?;
        order_id = ondo_order_id(ondo_result(&placed)?);
        if order_id.is_none() {
            for _ in 0..10 {
                order_id = ondo_test_open_order_id(&client, &client_id).await?;
                if order_id.is_some() {
                    break;
                }
                sleep(Duration::from_millis(500)).await;
            }
        }
        let id = order_id
            .as_ref()
            .ok_or_else(|| live_test_error("Ondo post-only order has no cancellable id"))?;
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_order",
            params(&[("orderID", id.as_str())]),
        )
        .await?;
        ondo_status(&cancel)?;
        let final_order = super::common::exchange_method_request(
            &client,
            "get_order",
            params(&[("orderID", id.as_str())]),
        )
        .await?;
        let final_data = ondo_result(&final_order)?;
        let filled = ondo_number(final_data, "filledSize").unwrap_or(0.0);
        if filled > 0.0 {
            ondo_close_until_flat(&client).await?;
            return Err(live_test_error("Ondo post-only order filled unexpectedly"));
        }
        if final_data.get("status").and_then(Value::as_str) != Some("canceled") {
            return Err(live_test_error(format!(
                "Ondo post-only order did not end canceled: {final_data}"
            )));
        }
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    let cleanup_result = ondo_cancel_test_order(&client, &client_id).await;
    let close_result = ondo_close_until_flat(&client).await;
    cleanup_result?;
    close_result?;
    lifecycle_result?;
    require_ondo_clean_account(&client).await
}

#[tokio::test]
#[ignore = "requires live exchange API access and real fills"]
async fn ondo_direct_live_fill_and_close() -> dcex::Result<()> {
    if !require_live_fill() {
        return Ok(());
    }
    let Some(keys) = require_env(&["ONDO_API_KEY_ID", "ONDO_API_SECRET"]) else {
        return Ok(());
    };
    let client = OndoClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    require_ondo_clean_account(&client).await?;
    let (size, _) = ondo_order_amounts(&client, true).await?;
    let client_id = unique_client_id("dcex-rs-fill-");
    let mut filled = 0.0;
    let mut buy_sent = false;
    let lifecycle_result = async {
        let buy = super::common::exchange_method_request(
            &client,
            "place_order",
            params(&[
                ("market", MARKET),
                ("side", "buy"),
                ("type", "market"),
                ("size", size.as_str()),
                ("clientOrderId", client_id.as_str()),
            ]),
        )
        .await?;
        buy_sent = true;
        let id = ondo_order_id(ondo_result(&buy)?)
            .ok_or_else(|| live_test_error("Ondo market buy returned no order id"))?;
        for _ in 0..20 {
            let order = super::common::exchange_method_request(
                &client,
                "get_order",
                params(&[("orderID", id.as_str())]),
            )
            .await?;
            filled = ondo_number(ondo_result(&order)?, "filledSize").unwrap_or(0.0);
            if filled > 0.0 {
                break;
            }
            sleep(Duration::from_millis(500)).await;
        }
        if filled <= 0.0 {
            return Err(live_test_error("Ondo market buy did not report a fill"));
        }
        ondo_close_until_flat(&client).await?;
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    if buy_sent {
        let close_result = ondo_close_until_flat(&client).await;
        close_result?;
    }
    lifecycle_result?;
    for _ in 0..20 {
        if ondo_rows(
            &super::common::exchange_method_request(&client, "get_positions", params(&[])).await?,
        )?
        .is_empty()
        {
            return Ok(());
        }
        sleep(Duration::from_millis(500)).await;
    }
    Err(live_test_error(
        "Ondo position remains after reduce-only close",
    ))
}

async fn require_ondo_clean_account(client: &OndoClient) -> dcex::Result<()> {
    let positions =
        super::common::exchange_method_request(client, "get_positions", params(&[])).await?;
    let orders =
        super::common::exchange_method_request(client, "get_open_orders", params(&[])).await?;
    if !ondo_rows(&positions)?.is_empty() || !ondo_rows(&orders)?.is_empty() {
        return Err(live_test_error(
            "Ondo live order test requires no positions or open orders",
        ));
    }
    Ok(())
}

async fn ondo_order_amounts(client: &OndoClient, crossing: bool) -> dcex::Result<(String, String)> {
    let markets =
        super::common::exchange_method_request(client, "get_markets", params(&[])).await?;
    let pairs = ondo_result(&markets)?
        .get("perps")
        .and_then(|perps| perps.get("tradingPairs"))
        .and_then(Value::as_array)
        .ok_or_else(|| live_test_error("Ondo markets response lacks perps tradingPairs"))?;
    let pair = pairs
        .iter()
        .find(|pair| {
            pair.get("market").and_then(Value::as_str) == Some(MARKET)
                && pair.get("disabled").and_then(Value::as_bool) != Some(true)
        })
        .ok_or_else(|| live_test_error("Ondo BTC perpetual market is unavailable"))?;
    let tick = ondo_number(pair, "quoteIncrement")
        .ok_or_else(|| live_test_error("Ondo quoteIncrement missing"))?;
    let step = ondo_number(pair, "baseIncrement")
        .ok_or_else(|| live_test_error("Ondo baseIncrement missing"))?;
    if tick <= 0.0 || step <= 0.0 {
        return Err(live_test_error("Ondo market increments must be positive"));
    }
    let depth = super::common::exchange_method_request(
        client,
        "get_depth",
        params(&[("market", MARKET), ("limit", "5")]),
    )
    .await?;
    let bid = ondo_result(&depth)?
        .get("bids")
        .and_then(Value::as_array)
        .and_then(|bids| bids.first())
        .and_then(Value::as_array)
        .and_then(|level| level.first())
        .and_then(value_f64)
        .ok_or_else(|| live_test_error("Ondo orderbook has no bid"))?;
    let ask = ondo_result(&depth)?
        .get("asks")
        .and_then(Value::as_array)
        .and_then(|asks| asks.first())
        .and_then(Value::as_array)
        .and_then(|level| level.first())
        .and_then(value_f64)
        .ok_or_else(|| live_test_error("Ondo orderbook has no ask"))?;
    if bid <= 0.0 || ask < bid {
        return Err(live_test_error("Ondo orderbook spread is invalid"));
    }
    let price = if crossing {
        bid
    } else {
        (bid * 0.95 / tick).floor() * tick
    };
    if price <= 0.0 {
        return Err(live_test_error("Ondo calculated order price is invalid"));
    }
    let size = ((10.0 / price / step).ceil() * step).max(step);
    if size * ask > 20.0 {
        return Err(live_test_error(format!(
            "Ondo minimum order exceeds 20 USD at the ask: {}",
            size * ask
        )));
    }
    Ok((format!("{size:.8}"), format!("{price:.8}")))
}

async fn ondo_close_until_flat(client: &OndoClient) -> dcex::Result<()> {
    for _ in 0..4 {
        let positions =
            super::common::exchange_method_request(client, "get_positions", params(&[])).await?;
        let position = ondo_rows(&positions)?
            .into_iter()
            .find(|position| position.get("market").and_then(Value::as_str) == Some(MARKET));
        let Some(position) = position else {
            return Ok(());
        };
        let size = ondo_number(position, "netQuantity")
            .ok_or_else(|| live_test_error("Ondo position has no netQuantity"))?;
        let side = match position.get("direction").and_then(Value::as_str) {
            Some("long") => "sell",
            Some("short") => "buy",
            other => {
                return Err(live_test_error(format!(
                    "Ondo position direction is invalid: {other:?}"
                )));
            }
        };
        let size = format!("{size:.8}");
        let close = super::common::exchange_method_request(
            client,
            "place_order",
            params(&[
                ("market", MARKET),
                ("side", side),
                ("type", "market"),
                ("size", size.as_str()),
                ("reduceOnly", "true"),
            ]),
        )
        .await?;
        ondo_status(&close)?;
        for _ in 0..10 {
            let positions =
                super::common::exchange_method_request(client, "get_positions", params(&[]))
                    .await?;
            if ondo_rows(&positions)?.is_empty() {
                return Ok(());
            }
            sleep(Duration::from_millis(500)).await;
        }
    }
    Err(live_test_error(
        "Ondo position remains after reduce-only close attempts",
    ))
}

async fn ondo_test_open_order_id(
    client: &OndoClient,
    client_id: &str,
) -> dcex::Result<Option<String>> {
    let orders = super::common::exchange_method_request(
        client,
        "get_open_orders",
        params(&[("market", MARKET)]),
    )
    .await?;
    Ok(ondo_rows(&orders)?
        .into_iter()
        .find(|order| order.get("clientOrderId").and_then(Value::as_str) == Some(client_id))
        .and_then(ondo_order_id))
}

async fn ondo_cancel_test_order(client: &OndoClient, client_id: &str) -> dcex::Result<()> {
    for _ in 0..10 {
        let id = ondo_test_open_order_id(client, client_id).await?;
        if let Some(id) = id {
            let cancel = super::common::exchange_method_request(
                client,
                "cancel_order",
                params(&[("orderID", id.as_str())]),
            )
            .await?;
            ondo_status(&cancel)?;
        }
        sleep(Duration::from_millis(500)).await;
        if ondo_test_open_order_id(client, client_id).await?.is_none() {
            return Ok(());
        }
    }
    Err(live_test_error(
        "Ondo test order remains open after cancellation",
    ))
}

fn ondo_result(response: &ValidatedResponse) -> dcex::Result<&Value> {
    ondo_status(response)?;
    response
        .data
        .get("result")
        .ok_or_else(|| live_test_error(format!("Ondo response has no result: {}", response.data)))
}

fn ondo_status(response: &ValidatedResponse) -> dcex::Result<()> {
    if !(200..300).contains(&response.status) || response.data.is_null() {
        return Err(live_test_error(format!(
            "Ondo HTTP request failed with status {}",
            response.status
        )));
    }
    if response.data.get("success").and_then(Value::as_bool) != Some(true) {
        return Err(live_test_error("Ondo API rejected request"));
    }
    Ok(())
}

fn ondo_rows(response: &ValidatedResponse) -> dcex::Result<Vec<&Value>> {
    ondo_result(response)?
        .as_array()
        .map(|rows| rows.iter().collect())
        .ok_or_else(|| live_test_error("Ondo response result is not a list"))
}

fn ondo_order_id(value: &Value) -> Option<String> {
    for key in ["orderID", "orderId", "id"] {
        if let Some(value) = value.get(key) {
            match value {
                Value::String(value) if !value.is_empty() => return Some(value.clone()),
                Value::Number(value) => return Some(value.to_string()),
                _ => {}
            }
        }
    }
    value.get("order").and_then(ondo_order_id)
}

fn ondo_number(value: &Value, key: &str) -> Option<f64> {
    value.get(key).and_then(value_f64)
}

fn value_f64(value: &Value) -> Option<f64> {
    value
        .as_f64()
        .or_else(|| value.as_str().and_then(|value| value.parse().ok()))
}
