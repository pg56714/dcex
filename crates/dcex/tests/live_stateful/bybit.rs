use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bybit::BybitClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    account_restriction, assert_success, asset_amount, contains_non_empty_array,
    fetch_trading_details, first_bid_price, format_transfer_amount_ceil, leveraged_margin_required,
    margin_target, minimum_order_quantity, params, parse_positive, post_only_buy_price, push,
    require_env, require_live_trading, require_order_id, sum_abs_values_for_symbols,
    wait_for_flat_position, wait_for_non_empty_records, wait_for_positive_position, BTC_USDT_SPOT,
    BTC_USDT_SWAP,
};

const BYBIT_SWAP_LEVERAGE: &str = "50";
const BYBIT_SWAP_LEVERAGE_VALUE: f64 = 50.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bybit_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BYBIT_API_KEY", "BYBIT_API_SECRET"]) else {
        return Ok(());
    };
    let client = BybitClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        true,
        Duration::from_secs(20),
    )?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Bybit, "bybit", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")?;
    let transferred = match ensure_unified_usdt(&client, required_usdt * 1.01).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("qty", quantity.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_bybit_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await;
    return_bybit_transfer(&client, transferred).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bybit_swap_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BYBIT_API_KEY", "BYBIT_API_SECRET"]) else {
        return Ok(());
    };
    let client = BybitClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        true,
        Duration::from_secs(20),
    )?;

    if bybit_open_swap_orders(&client).await? {
        eprintln!("skipping Bybit swap live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }
    let position_response = super::common::exchange_method_request(
        &client,
        "get_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    if bybit_swap_position_abs_from(&position_response.data) > 0.0 {
        eprintln!("skipping Bybit swap live stateful order; BTC-USDT swap position exists");
        return Ok(());
    }
    let position_idx = bybit_long_position_idx(&position_response.data);

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_orderbook",
        params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Bybit, "bybit", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    set_bybit_swap_leverage(&client).await?;
    let market_price_estimate = first_bid_price(&orderbook.data)?;
    let required_usdt = leveraged_margin_required(
        market_price_estimate,
        &quantity,
        &details,
        BYBIT_SWAP_LEVERAGE_VALUE,
    )?;
    let transferred = match ensure_unified_usdt(&client, margin_target(required_usdt)).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let mut order_params = params(&[
        ("product_symbol", BTC_USDT_SWAP),
        ("qty", quantity.as_str()),
        ("price", price.as_str()),
    ]);
    if let Some(position_idx) = position_idx {
        push(&mut order_params, "positionIdx", position_idx);
    }
    let order_result = super::common::exchange_method_request(
        &client,
        "place_post_only_limit_buy_order",
        order_params,
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_bybit_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await;
    match cancel_result {
        Ok(cancel) => assert_success(&cancel),
        Err(error)
            if account_restriction(
                &error,
                &["110001", "order not exists", "too late to cancel"],
            ) =>
        {
            if bybit_open_swap_orders(&client).await?
                || bybit_swap_position_abs(&client).await? > 0.0
            {
                return Err(error);
            }
            eprintln!("Bybit swap post-only order was already absent before cancel");
        }
        Err(error) => {
            return_bybit_transfer(&client, transferred).await?;
            return Err(error);
        }
    }

    let mut open_params = params(&[
        ("product_symbol", BTC_USDT_SWAP),
        ("qty", quantity.as_str()),
    ]);
    if let Some(position_idx) = position_idx {
        push(&mut open_params, "positionIdx", position_idx);
    }
    let open_result =
        super::common::exchange_method_request(&client, "place_market_buy_order", open_params)
            .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) => {
            return_bybit_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&opened);
    let opened_id = require_order_id(&opened.data, &["orderId"])?;
    eprintln!("Bybit swap market open orderId={opened_id}");
    assert!(wait_for_positive_position(|| bybit_swap_position_abs(&client)).await? > 0.0);

    let mut close_params = params(&[
        ("product_symbol", BTC_USDT_SWAP),
        ("qty", quantity.as_str()),
        ("reduceOnly", "true"),
    ]);
    if let Some(position_idx) = position_idx {
        push(&mut close_params, "positionIdx", position_idx);
    }
    let closed =
        super::common::exchange_method_request(&client, "place_market_sell_order", close_params)
            .await?;
    assert_success(&closed);
    let closed_id = require_order_id(&closed.data, &["orderId"])?;
    eprintln!("Bybit swap market close orderId={closed_id}");
    assert_eq!(
        wait_for_flat_position(|| bybit_swap_position_abs(&client)).await?,
        0.0
    );
    assert_bybit_swap_records(&client, &opened_id, &closed_id).await?;

    return_bybit_transfer(&client, transferred).await?;
    Ok(())
}

async fn ensure_unified_usdt(client: &BybitClient, required: f64) -> dcex::Result<Option<f64>> {
    let unified = account_usdt(client, "UNIFIED").await?;
    if unified >= required {
        return Ok(Some(0.0));
    }
    let needed = required - unified;
    if account_usdt(client, "FUND").await? < needed {
        eprintln!(
            "skipping Bybit live stateful order; insufficient transferable USDT, required={required:.8}, unified={unified:.8}"
        );
        return Ok(None);
    }
    let amount = format_transfer_amount_ceil(needed, 4);
    let response = super::common::exchange_method_request(
        &client,
        "create_internal_transfer",
        params(&[
            ("coin", "USDT"),
            ("amount", amount.as_str()),
            ("fromAccountType", "FUND"),
            ("toAccountType", "UNIFIED"),
        ]),
    )
    .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_bybit_transfer(client: &BybitClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let available = account_usdt(client, "UNIFIED").await?;
    let amount = format_transfer_amount_ceil(amount.min(available), 4);
    if amount == "0" {
        return Ok(());
    }
    let response = super::common::exchange_method_request(
        &client,
        "create_internal_transfer",
        params(&[
            ("coin", "USDT"),
            ("amount", amount.as_str()),
            ("fromAccountType", "UNIFIED"),
            ("toAccountType", "FUND"),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

async fn account_usdt(client: &BybitClient, account_type: &str) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_coin_balance",
        params(&[("accountType", account_type), ("coin", "USDT")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &[
            "transferBalance",
            "walletBalance",
            "availableToWithdraw",
            "availableBalance",
        ],
    ))
}

async fn bybit_open_swap_orders(client: &BybitClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_open_orders",
        params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "20")]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["list"]))
}

async fn bybit_swap_position_abs(client: &BybitClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(bybit_swap_position_abs_from(&response.data))
}

async fn set_bybit_swap_leverage(client: &BybitClient) -> dcex::Result<()> {
    match super::common::exchange_method_request(
        &client,
        "set_leverage",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("leverage", BYBIT_SWAP_LEVERAGE),
        ]),
    )
    .await
    {
        Ok(response) => {
            assert_success(&response);
            Ok(())
        }
        Err(error) if error.to_string().contains("110043") => Ok(()),
        Err(error) => Err(error),
    }
}

async fn assert_bybit_swap_records(
    client: &BybitClient,
    opened_id: &str,
    closed_id: &str,
) -> dcex::Result<()> {
    let has_opened_history = wait_for_bybit_order_history(client, opened_id).await?;
    assert!(
        has_opened_history,
        "Bybit opened market order was not found in order history"
    );

    let has_closed_history = wait_for_bybit_order_history(client, closed_id).await?;
    assert!(
        has_closed_history,
        "Bybit closed market order was not found in order history"
    );

    let has_execution = wait_for_non_empty_records(
        || {
            super::common::exchange_method_request(
                &client,
                "get_execution_list",
                params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "20")]),
            )
        },
        &["list"],
    )
    .await?;
    assert!(
        has_execution,
        "Bybit swap execution list did not return fills"
    );
    Ok(())
}

async fn wait_for_bybit_order_history(client: &BybitClient, order_id: &str) -> dcex::Result<bool> {
    wait_for_non_empty_records(
        || {
            super::common::exchange_method_request(
                &client,
                "get_order_history",
                params(&[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("orderId", order_id),
                    ("limit", "20"),
                ]),
            )
        },
        &["list"],
    )
    .await
}

fn bybit_swap_position_abs_from(data: &Value) -> f64 {
    sum_abs_values_for_symbols(data, &["symbol"], &["BTCUSDT"], &["size"])
}

fn bybit_long_position_idx(data: &Value) -> Option<&'static str> {
    if bybit_has_position_idx(data, "1") || bybit_has_position_idx(data, "2") {
        Some("1")
    } else {
        None
    }
}

fn bybit_has_position_idx(data: &Value, expected: &str) -> bool {
    match data {
        Value::Object(object) => {
            object
                .get("positionIdx")
                .and_then(|value| match value {
                    Value::Number(value) => Some(value.to_string()),
                    Value::String(value) => Some(value.clone()),
                    _ => None,
                })
                .is_some_and(|value| value == expected)
                || object
                    .values()
                    .any(|value| bybit_has_position_idx(value, expected))
        }
        Value::Array(values) => values
            .iter()
            .any(|value| bybit_has_position_idx(value, expected)),
        _ => false,
    }
}
