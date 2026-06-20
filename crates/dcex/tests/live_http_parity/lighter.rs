use std::time::Duration;

use dcex::exchanges::lighter::LighterClient;

use super::common::{require_env, run_cases, run_private_cases, Case, BTC_USDT_SWAP};

const LIGHTER_BASE_URL: &str = "https://mainnet.zklighter.elliot.ai";

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn lighter_public_live_parity() -> dcex::Result<()> {
    let client = LighterClient::new(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new("get_status", &[]),
            Case::new("get_info", &[]),
            Case::new("get_order_book_details", &[]),
            Case::new("get_order_books", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_order_book_orders",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "5")],
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
                        get_next_nonce
                    ]
                )
            }
        },
    )
    .await
}
