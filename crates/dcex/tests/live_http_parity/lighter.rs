use std::time::Duration;

use dcex::exchanges::lighter::LighterClient;
use serde_json::Value;

use super::common::{live_http_enabled, require_env, run_cases, run_private_cases, Case};

const LIGHTER_BASE_URL: &str = "https://mainnet.zklighter.elliot.ai";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn lighter_public_live_parity() -> dcex::Result<()> {
    let client = LighterClient::new(Duration::from_secs(20))?;
    if !live_http_enabled() {
        eprintln!("skipping live HTTP parity test; set RUN_LIVE_HTTP_TESTS=1");
        return Ok(());
    }
    let details = client.get_order_book_details().await?;
    let market_id = active_market_id(&details.data)?;
    run_cases(
        vec![
            Case::new("get_status", &[]),
            Case::new("get_info", &[]),
            Case::new("get_order_book_details", &[]),
            Case::new("get_order_books", &[("market_id", market_id.as_str())]),
            Case::new(
                "get_order_book_orders",
                &[("market_id", market_id.as_str()), ("limit", "5")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_info,
                        get_order_book_details,
                        get_order_book_orders,
                        get_order_books,
                        get_status,
                    ]
                )
            }
        },
    )
    .await
}

fn active_market_id(data: &Value) -> dcex::Result<String> {
    let markets = data
        .get("order_book_details")
        .and_then(Value::as_array)
        .ok_or_else(|| {
            dcex::DcexError::Decode(format!("missing Lighter order_book_details: {data:?}"))
        })?;
    let market = markets
        .iter()
        .find(|market| market.get("status").and_then(Value::as_str) == Some("active"))
        .or_else(|| markets.first())
        .ok_or_else(|| dcex::DcexError::Decode("no Lighter market found".to_string()))?;
    market
        .get("market_id")
        .and_then(|value| match value {
            Value::String(value) => Some(value.clone()),
            Value::Number(value) => Some(value.to_string()),
            _ => None,
        })
        .ok_or_else(|| dcex::DcexError::Decode(format!("missing Lighter market_id: {market:?}")))
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn lighter_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&[
        "LIGHTER_ACCOUNT_INDEX",
        "LIGHTER_API_KEY_INDEX",
        "LIGHTER_API_PRIVATE_KEY",
    ]) else {
        return Ok(());
    };
    let account_index = keys[0].parse::<u64>().map_err(|error| {
        dcex::DcexError::InvalidInput(format!("invalid LIGHTER_ACCOUNT_INDEX: {error}"))
    })?;
    let api_key_index = keys[1].parse::<u64>().map_err(|error| {
        dcex::DcexError::InvalidInput(format!("invalid LIGHTER_API_KEY_INDEX: {error}"))
    })?;
    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(20),
        LIGHTER_BASE_URL.to_string(),
        Some(account_index),
        Some(api_key_index),
        Some(keys[2].clone()),
    )?;
    run_private_cases(
        &[
            "LIGHTER_ACCOUNT_INDEX",
            "LIGHTER_API_KEY_INDEX",
            "LIGHTER_API_PRIVATE_KEY",
        ],
        vec![
            Case::new("get_next_nonce", &[]),
            Case::new(
                "get_account_active_orders",
                &[("account_index", keys[0].as_str())],
            ),
            Case::new("get_account_limits", &[("account_index", keys[0].as_str())]),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_account_active_orders,
                        get_account_limits,
                        get_next_nonce,
                    ]
                )
            }
        },
    )
    .await
}
