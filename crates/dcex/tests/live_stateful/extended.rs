use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::extended::ExtendedClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    format_step_decimal, live_test_error, optional_env, params, require_env, require_live_fill,
    require_live_trading, round_down_to_step, round_up_to_step,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn extended_direct_live_order_and_optional_fill() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "EXTENDED_API_KEY",
        "EXTENDED_STARK_PRIVATE_KEY",
        "EXTENDED_STARK_PUBLIC_KEY",
        "EXTENDED_VAULT_NUMBER",
    ]) else {
        return Ok(());
    };
    let vault_number = keys[3]
        .parse::<u64>()
        .map_err(|error| live_test_error(format!("invalid EXTENDED_VAULT_NUMBER: {error}")))?;
    let client = ExtendedClient::with_base_url_and_stark(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Some(vault_number),
        optional_env("EXTENDED_CLIENT_ID"),
        Duration::from_secs(20),
        "https://api.starknet.extended.exchange".to_string(),
        "dcex-rust/0.1".to_string(),
    )?;
    extended_require_clean(&client).await?;
    let (market, quantity, step, tick) = extended_test_market(&client).await?;
    let (bid, ask) = extended_book_prices(&client, &market).await?;
    let post_price = format_step_decimal(round_down_to_step(bid * 0.99, tick), tick)?;
    let size = format_step_decimal(quantity, step)?;
    let mut post_order_id = None;
    let post_result = async {
        let order = super::common::exchange_method_request(
            &client,
            "place_limit_order",
            params(&[
                ("market", market.as_str()),
                ("side", "BUY"),
                ("qty", size.as_str()),
                ("price", post_price.as_str()),
                ("postOnly", "true"),
                ("timeInForce", "GTT"),
            ]),
        )
        .await?;
        let id = extended_order_id(extended_data(&order)?)?;
        post_order_id = Some(id.clone());
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_order",
            params(&[("id", id.as_str())]),
        )
        .await?;
        extended_status(&cancel)?;
        for _ in 0..20 {
            let orders = super::common::exchange_method_request(
                &client,
                "get_open_orders",
                params(&[("market", market.as_str())]),
            )
            .await?;
            if extended_data(&orders)?
                .as_array()
                .is_some_and(|orders| orders.is_empty())
            {
                break;
            }
            sleep(Duration::from_millis(500)).await;
        }
        let order = super::common::exchange_method_request(
            &client,
            "get_order",
            params(&[("id", id.as_str())]),
        )
        .await?;
        let order = extended_data(&order)?;
        if extended_number(order, "filledQty").unwrap_or(0.0) > 0.0 {
            extended_close_until_flat(&client, &market, step, tick).await?;
            return Err(live_test_error(
                "Extended post-only order filled unexpectedly",
            ));
        }
        if order.get("status").and_then(Value::as_str) != Some("CANCELLED") {
            return Err(live_test_error(format!(
                "Extended post-only order did not cancel: {order}"
            )));
        }
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    let cancel_result = if let Some(id) = post_order_id.as_deref() {
        extended_cancel_if_open(&client, &market, id).await
    } else {
        Ok(())
    };
    let close_result = extended_close_until_flat(&client, &market, step, tick).await;
    cancel_result?;
    close_result?;
    post_result?;
    extended_require_clean(&client).await?;
    if !require_live_fill() {
        return Ok(());
    }

    let crossing_price = format_step_decimal(round_up_to_step(ask * 1.005, tick), tick)?;
    let mut buy_sent = false;
    let fill_result = async {
        let buy = super::common::exchange_method_request(
            &client,
            "place_limit_order",
            params(&[
                ("market", market.as_str()),
                ("side", "BUY"),
                ("qty", size.as_str()),
                ("price", crossing_price.as_str()),
                ("postOnly", "false"),
                ("timeInForce", "IOC"),
            ]),
        )
        .await?;
        extended_data(&buy)?;
        buy_sent = true;
        let mut filled = false;
        for _ in 0..20 {
            let positions = super::common::exchange_method_request(
                &client,
                "get_positions",
                params(&[("market", market.as_str())]),
            )
            .await?;
            filled = extended_data(&positions)?
                .as_array()
                .is_some_and(|positions| !positions.is_empty());
            if filled {
                break;
            }
            sleep(Duration::from_millis(500)).await;
        }
        if !filled {
            return Err(live_test_error(
                "Extended IOC buy did not create a position",
            ));
        }
        extended_close_until_flat(&client, &market, step, tick).await?;
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    if buy_sent {
        extended_close_until_flat(&client, &market, step, tick).await?;
    }
    fill_result?;
    extended_require_clean(&client).await
}

async fn extended_require_clean(client: &ExtendedClient) -> dcex::Result<()> {
    let orders =
        super::common::exchange_method_request(client, "get_open_orders", params(&[])).await?;
    let positions =
        super::common::exchange_method_request(client, "get_positions", params(&[])).await?;
    if !extended_rows(&orders)?.is_empty() || !extended_rows(&positions)?.is_empty() {
        return Err(live_test_error(
            "Extended live test requires an account without open orders or positions",
        ));
    }
    Ok(())
}

async fn extended_test_market(client: &ExtendedClient) -> dcex::Result<(String, f64, f64, f64)> {
    let response =
        super::common::exchange_method_request(client, "get_markets", params(&[])).await?;
    for market in extended_rows(&response)? {
        if market.get("type").and_then(Value::as_str) != Some("PERPETUAL")
            || market.get("status").and_then(Value::as_str) != Some("ACTIVE")
            || market.get("isRfq").and_then(Value::as_bool) == Some(true)
            || market.get("isOffHours").and_then(Value::as_bool) == Some(true)
        {
            continue;
        }
        let Some(name) = market.get("name").and_then(Value::as_str) else {
            continue;
        };
        let Some(config) = market.get("tradingConfig") else {
            continue;
        };
        let (Some(minimum), Some(step), Some(tick)) = (
            extended_number(config, "minOrderSize"),
            extended_number(config, "minOrderSizeChange"),
            extended_number(config, "minPriceChange"),
        ) else {
            continue;
        };
        if minimum <= 0.0 || step <= 0.0 || tick <= 0.0 {
            continue;
        }
        let quantity = round_up_to_step(minimum, step);
        let Ok((_, ask)) = extended_book_prices(client, name).await else {
            continue;
        };
        if quantity * ask * 1.005 <= 25.0 {
            return Ok((name.to_string(), quantity, step, tick));
        }
    }
    Err(live_test_error(
        "Extended has no active, liquid perpetual with a minimum order at most 25 USD",
    ))
}

async fn extended_book_prices(client: &ExtendedClient, market: &str) -> dcex::Result<(f64, f64)> {
    let response = super::common::exchange_method_request(
        client,
        "get_order_book",
        params(&[("market", market)]),
    )
    .await?;
    let data = extended_data(&response)?;
    let price = |side: &str| {
        data.get(side)
            .and_then(Value::as_array)
            .and_then(|levels| levels.first())
            .and_then(|level| extended_number(level, "price"))
    };
    let bid = price("bid").ok_or_else(|| live_test_error("Extended orderbook has no bid"))?;
    let ask = price("ask").ok_or_else(|| live_test_error("Extended orderbook has no ask"))?;
    if bid <= 0.0 || ask <= bid {
        return Err(live_test_error("Extended orderbook spread is invalid"));
    }
    Ok((bid, ask))
}

async fn extended_cancel_if_open(
    client: &ExtendedClient,
    market: &str,
    id: &str,
) -> dcex::Result<()> {
    for _ in 0..10 {
        let orders = super::common::exchange_method_request(
            client,
            "get_open_orders",
            params(&[("market", market)]),
        )
        .await?;
        let open = extended_rows(&orders)?
            .into_iter()
            .any(|order| extended_order_id(order).ok().as_deref() == Some(id));
        if !open {
            return Ok(());
        }
        let cancel =
            super::common::exchange_method_request(client, "cancel_order", params(&[("id", id)]))
                .await?;
        extended_status(&cancel)?;
        sleep(Duration::from_millis(500)).await;
    }
    Err(live_test_error("Extended test order remains open"))
}

async fn extended_close_until_flat(
    client: &ExtendedClient,
    market: &str,
    step: f64,
    tick: f64,
) -> dcex::Result<()> {
    for _ in 0..4 {
        let response = super::common::exchange_method_request(
            client,
            "get_positions",
            params(&[("market", market)]),
        )
        .await?;
        let positions = extended_rows(&response)?;
        if positions.is_empty() {
            return Ok(());
        }
        let (bid, ask) = extended_book_prices(client, market).await?;
        for position in positions {
            let qty = extended_number(position, "size")
                .ok_or_else(|| live_test_error("Extended position has no size"))?;
            let (side, price) = match position.get("side").and_then(Value::as_str) {
                Some("LONG") => ("SELL", round_down_to_step(bid * 0.995, tick)),
                Some("SHORT") => ("BUY", round_up_to_step(ask * 1.005, tick)),
                other => {
                    return Err(live_test_error(format!(
                        "Extended position side is invalid: {other:?}"
                    )))
                }
            };
            let qty = format_step_decimal(qty, step)?;
            let price = format_step_decimal(price, tick)?;
            let close = super::common::exchange_method_request(
                client,
                "place_limit_order",
                params(&[
                    ("market", market),
                    ("side", side),
                    ("qty", qty.as_str()),
                    ("price", price.as_str()),
                    ("reduceOnly", "true"),
                    ("timeInForce", "IOC"),
                ]),
            )
            .await?;
            extended_data(&close)?;
        }
        sleep(Duration::from_secs(1)).await;
    }
    Err(live_test_error(
        "Extended position remains after reduce-only IOC attempts",
    ))
}

fn extended_data(response: &ValidatedResponse) -> dcex::Result<&Value> {
    extended_status(response)?;
    response
        .data
        .get("data")
        .ok_or_else(|| live_test_error(format!("Extended response has no data: {}", response.data)))
}

fn extended_status(response: &ValidatedResponse) -> dcex::Result<()> {
    if !(200..300).contains(&response.status) || response.data.is_null() {
        return Err(live_test_error(format!(
            "Extended HTTP request failed with status {}",
            response.status
        )));
    }
    if response.data.get("status").and_then(Value::as_str) != Some("OK") {
        return Err(live_test_error("Extended API rejected request"));
    }
    Ok(())
}

fn extended_rows(response: &ValidatedResponse) -> dcex::Result<Vec<&Value>> {
    extended_data(response)?
        .as_array()
        .map(|rows| rows.iter().collect())
        .ok_or_else(|| live_test_error("Extended response data is not a list"))
}

fn extended_order_id(data: &Value) -> dcex::Result<String> {
    data.get("id")
        .and_then(|id| match id {
            Value::String(id) => Some(id.clone()),
            Value::Number(id) => Some(id.to_string()),
            _ => None,
        })
        .ok_or_else(|| live_test_error(format!("Extended order has no id: {data}")))
}

fn extended_number(value: &Value, key: &str) -> Option<f64> {
    value.get(key).and_then(|value| {
        value
            .as_f64()
            .or_else(|| value.as_str().and_then(|value| value.parse().ok()))
    })
}
