use std::time::Duration;

use dcex::exchanges::lighter::{
    credential_env_names, LighterClient, LighterCredentials, LighterNetwork,
};
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    assert_success, find_f64, find_string, live_test_error, require_env, require_live_trading,
    unique_client_id,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn lighter_mainnet_direct_live_stateful_order() -> dcex::Result<()> {
    lighter_direct_live_stateful_order(LighterNetwork::Mainnet).await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn lighter_robinhood_direct_live_stateful_order() -> dcex::Result<()> {
    lighter_direct_live_stateful_order(LighterNetwork::Robinhood).await
}

async fn lighter_direct_live_stateful_order(network: LighterNetwork) -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let env_names = credential_env_names(network);
    let Some(keys) = require_env(&env_names) else {
        return Ok(());
    };
    let account_index = parse_u64(&keys[0], env_names[0])?;
    let api_key_index = parse_u64(&keys[1], env_names[1])?;
    let credentials = LighterCredentials::new(account_index, api_key_index, keys[2].clone())?;
    let client = LighterClient::with_credentials(Duration::from_secs(20), network, credentials)?;
    if let Some(message) = client.check_client().await? {
        return Err(live_test_error(format!(
            "Lighter live stateful order client check failed: {message}"
        )));
    }
    cleanup_lighter_state(&client, account_index).await?;

    let market = active_lighter_market(&client).await?;
    let market_id = value_string(&market, "market_id")?;
    let client_order_index = unique_client_id("").parse::<i64>().map_err(|error| {
        dcex::DcexError::InvalidInput(format!("invalid generated Lighter client id: {error}"))
    })?;
    let order_book = super::common::exchange_method_request(
        &client,
        "get_order_book_orders",
        vec![
            ("market_id".to_string(), market_id.clone()),
            ("limit".to_string(), "5".to_string()),
        ],
    )
    .await?;
    let best_bid = first_lighter_book_price(&order_book.data, "bids")?;
    let (base_amount, price) = post_only_buy_order_amounts(&market, best_bid)?;
    let order_result = super::common::exchange_method_request(
        &client,
        "create_order",
        vec![
            ("market_index".to_string(), market_id.clone()),
            (
                "client_order_index".to_string(),
                client_order_index.to_string(),
            ),
            ("base_amount".to_string(), base_amount.to_string()),
            ("price".to_string(), price.to_string()),
            ("is_ask".to_string(), "false".to_string()),
            ("order_type".to_string(), "0".to_string()),
            ("time_in_force".to_string(), "2".to_string()),
            ("order_expiry".to_string(), "-1".to_string()),
        ],
    )
    .await;

    let lifecycle_result = async {
        let order = order_result?;
        ensure_lighter_success(&order, "create order")?;
        sleep(Duration::from_secs(1)).await;
        let order_index =
            active_order_index(&client, account_index, &market_id, client_order_index).await?;
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_order",
            vec![
                ("market_index".to_string(), market_id),
                ("order_index".to_string(), order_index),
            ],
        )
        .await?;
        ensure_lighter_success(&cancel, "cancel order")?;
        Ok::<_, dcex::DcexError>((order, cancel))
    }
    .await;

    let cleanup_result = cleanup_lighter_state(&client, account_index).await;
    cleanup_result?;
    let (order, cancel) = lifecycle_result?;
    assert_success(&order);
    assert_success(&cancel);
    Ok(())
}

fn ensure_lighter_success(
    response: &dcex::exchange::ValidatedResponse,
    action: &str,
) -> dcex::Result<()> {
    if !(200..300).contains(&response.status) {
        return Err(live_test_error(format!(
            "Lighter {action} returned HTTP {}: {}",
            response.status, response.data
        )));
    }
    if let Some(code) = response.data.get("code").and_then(value_f64) {
        if code != 0.0 && code != 200.0 {
            return Err(live_test_error(format!(
                "Lighter {action} returned code {code}: {}",
                response.data
            )));
        }
    }
    Ok(())
}

async fn cleanup_lighter_state(client: &LighterClient, account_index: u64) -> dcex::Result<()> {
    for _ in 0..10 {
        cleanup_lighter_state_once(client, account_index).await?;
        sleep(Duration::from_secs(1)).await;
        if lighter_account_is_clean(client, account_index).await? {
            return Ok(());
        }
    }
    Err(live_test_error(
        "Lighter orders or positions still exist after cleanup",
    ))
}

async fn cleanup_lighter_state_once(
    client: &LighterClient,
    account_index: u64,
) -> dcex::Result<()> {
    let active = super::common::exchange_method_request(
        client,
        "get_account_active_orders",
        vec![("account_index".to_string(), account_index.to_string())],
    )
    .await?;
    for order in active
        .data
        .get("orders")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let market_id =
            value_string(order, "market_id").or_else(|_| value_string(order, "market_index"))?;
        let order_index = value_string(order, "order_index")?;
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_order",
            vec![
                ("market_index".to_string(), market_id),
                ("order_index".to_string(), order_index),
            ],
        )
        .await?;
        assert_success(&cancel);
    }

    let account = super::common::exchange_method_request(
        client,
        "get_account",
        vec![
            ("by".to_string(), "index".to_string()),
            ("value".to_string(), account_index.to_string()),
        ],
    )
    .await?;
    let details = client.get_order_book_details().await?;
    let markets = details
        .data
        .get("order_book_details")
        .and_then(Value::as_array)
        .ok_or_else(|| {
            dcex::DcexError::Decode(format!("missing Lighter order_book_details: {details:?}"))
        })?;

    for position in lighter_positions(&account.data) {
        let market_id = value_string(position, "market_id")?;
        let signed_size = signed_lighter_position_size(position)?;
        if signed_size == 0.0 {
            continue;
        }
        let market = markets
            .iter()
            .find(|market| value_string(market, "market_id").ok().as_deref() == Some(&market_id))
            .ok_or_else(|| {
                dcex::DcexError::Decode(format!("missing Lighter market {market_id}"))
            })?;
        close_lighter_position(client, market, signed_size).await?;
    }

    Ok(())
}

async fn lighter_account_is_clean(
    client: &LighterClient,
    account_index: u64,
) -> dcex::Result<bool> {
    let active = super::common::exchange_method_request(
        client,
        "get_account_active_orders",
        vec![("account_index".to_string(), account_index.to_string())],
    )
    .await?;
    let has_active_orders = active
        .data
        .get("orders")
        .and_then(Value::as_array)
        .is_some_and(|orders| !orders.is_empty());

    let account = super::common::exchange_method_request(
        client,
        "get_account",
        vec![
            ("by".to_string(), "index".to_string()),
            ("value".to_string(), account_index.to_string()),
        ],
    )
    .await?;
    let has_positions = lighter_positions(&account.data)
        .iter()
        .any(|position| signed_lighter_position_size(position).unwrap_or(0.0) != 0.0);
    Ok(!has_active_orders && !has_positions)
}

async fn close_lighter_position(
    client: &LighterClient,
    market: &Value,
    signed_size: f64,
) -> dcex::Result<()> {
    let market_id = value_string(market, "market_id")?;
    let price_decimals = value_u32(market, "price_decimals")?;
    let size_decimals = value_u32(market, "size_decimals")?;
    let min_base = value_f64_required(market, "min_base_amount")?;
    let base = signed_size.abs().max(min_base);
    let base_amount = scale_amount(base, size_decimals, true)?;
    let book = super::common::exchange_method_request(
        client,
        "get_order_book_orders",
        vec![
            ("market_id".to_string(), market_id.clone()),
            ("limit".to_string(), "5".to_string()),
        ],
    )
    .await?;
    let bid = first_lighter_book_price(&book.data, "bids")?;
    let ask = first_lighter_book_price(&book.data, "asks")?;
    let (is_ask, price) = if signed_size > 0.0 {
        (
            true,
            scale_amount((bid * 0.995).max(0.0), price_decimals, false)?,
        )
    } else {
        (false, scale_amount(ask * 1.005, price_decimals, true)?)
    };
    let close = super::common::exchange_method_request(
        client,
        "create_order",
        vec![
            ("market_index".to_string(), market_id),
            (
                "client_order_index".to_string(),
                unique_client_id("").to_string(),
            ),
            ("base_amount".to_string(), base_amount.to_string()),
            ("price".to_string(), price.to_string()),
            ("is_ask".to_string(), is_ask.to_string()),
            ("order_type".to_string(), "1".to_string()),
            ("time_in_force".to_string(), "0".to_string()),
            ("reduce_only".to_string(), "true".to_string()),
            ("order_expiry".to_string(), "0".to_string()),
        ],
    )
    .await?;
    assert_success(&close);
    Ok(())
}

fn lighter_positions(data: &Value) -> Vec<&Value> {
    data.get("accounts")
        .and_then(Value::as_array)
        .and_then(|accounts| accounts.first())
        .and_then(|account| account.get("positions"))
        .and_then(Value::as_array)
        .map(|positions| positions.iter().collect())
        .unwrap_or_default()
}

fn signed_lighter_position_size(position: &Value) -> dcex::Result<f64> {
    let size = find_f64(position, &["position"]).unwrap_or(0.0);
    let sign = find_f64(position, &["sign"]).unwrap_or(1.0);
    Ok(if sign < 0.0 { -size } else { size })
}

fn first_lighter_book_price(data: &Value, key: &str) -> dcex::Result<f64> {
    data.get(key)
        .and_then(Value::as_array)
        .and_then(|levels| levels.first())
        .and_then(|level| level.get("price"))
        .and_then(value_f64)
        .ok_or_else(|| dcex::DcexError::Decode(format!("missing Lighter {key} price: {data}")))
}

async fn active_lighter_market(client: &LighterClient) -> dcex::Result<Value> {
    let response = client.get_order_book_details().await?;
    let markets = response
        .data
        .get("order_book_details")
        .and_then(Value::as_array)
        .ok_or_else(|| {
            dcex::DcexError::Decode(format!("missing Lighter order_book_details: {response:?}"))
        })?;
    markets
        .iter()
        .find(|market| {
            market.get("status").and_then(Value::as_str) == Some("active")
                && market
                    .get("last_trade_price")
                    .and_then(value_f64)
                    .is_some_and(|price| price > 0.0)
        })
        .cloned()
        .ok_or_else(|| dcex::DcexError::Decode("no active Lighter market found".to_string()))
}

fn post_only_buy_order_amounts(market: &Value, best_bid: f64) -> dcex::Result<(i64, i64)> {
    let price_decimals = value_u32(market, "price_decimals")?;
    let size_decimals = value_u32(market, "size_decimals")?;
    let min_base = value_f64_required(market, "min_base_amount")?;
    let min_quote = value_f64_required(market, "min_quote_amount")?;
    let price_step = 1.0 / 10_f64.powi(price_decimals as i32);
    let price = scale_amount(
        (best_bid - price_step)
            .min(best_bid * 0.999)
            .max(price_step),
        price_decimals,
        false,
    )?;
    let price_float = (price as f64) / 10_f64.powi(price_decimals as i32);
    let min_size = 1.0 / 10_f64.powi(size_decimals as i32);
    let base = min_base.max(min_quote / price_float).max(min_size);
    let base_amount = scale_amount(base, size_decimals, true)?;
    Ok((base_amount, price))
}

async fn active_order_index(
    client: &LighterClient,
    account_index: u64,
    market_id: &str,
    client_order_index: i64,
) -> dcex::Result<String> {
    for _ in 0..30 {
        let active = super::common::exchange_method_request(
            &client,
            "get_account_active_orders",
            vec![
                ("account_index".to_string(), account_index.to_string()),
                ("market_id".to_string(), market_id.to_string()),
            ],
        )
        .await?;
        if let Some(order_index) = find_string(&active.data, &["order_index", "orderIndex"]) {
            if find_string(&active.data, &["client_order_index", "clientOrderIndex"]).as_deref()
                == Some(&client_order_index.to_string())
            {
                return Ok(order_index);
            }
        }
        sleep(Duration::from_millis(500)).await;
    }
    Err(dcex::DcexError::Decode(format!(
        "Lighter active order not found for client_order_index={client_order_index}"
    )))
}

fn parse_u64(value: &str, name: &str) -> dcex::Result<u64> {
    value
        .parse::<u64>()
        .map_err(|error| dcex::DcexError::InvalidInput(format!("invalid {name}: {error}")))
}

fn value_string(value: &Value, key: &str) -> dcex::Result<String> {
    value
        .get(key)
        .and_then(|value| match value {
            Value::String(value) => Some(value.clone()),
            Value::Number(value) => Some(value.to_string()),
            _ => None,
        })
        .ok_or_else(|| dcex::DcexError::Decode(format!("missing {key}: {value}")))
}

fn value_u32(value: &Value, key: &str) -> dcex::Result<u32> {
    value_f64_required(value, key).map(|value| value as u32)
}

fn value_f64_required(value: &Value, key: &str) -> dcex::Result<f64> {
    value.get(key).and_then(value_f64).ok_or_else(|| {
        dcex::DcexError::Decode(format!("missing numeric Lighter field {key}: {value}"))
    })
}

fn value_f64(value: &Value) -> Option<f64> {
    match value {
        Value::Number(value) => value.as_f64(),
        Value::String(value) => value.parse().ok(),
        _ => None,
    }
}

fn scale_amount(value: f64, decimals: u32, ceil: bool) -> dcex::Result<i64> {
    if !value.is_finite() || value <= 0.0 {
        return Err(dcex::DcexError::Decode(format!(
            "invalid Lighter scaled value: {value}"
        )));
    }
    let scaled = value * 10_f64.powi(decimals as i32);
    Ok(if ceil { scaled.ceil() } else { scaled.floor() } as i64)
}
