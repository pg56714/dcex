use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitget::BitgetClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, bitget_unified_account_error, contains_non_empty_array,
    fetch_trading_details, minimum_order_quantity, params, post_only_buy_price, push, require_env,
    require_live_trading, require_order_id, sum_abs_values_for_symbols, unique_client_id,
    wait_for_flat_position, wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const BITGET_FUTURES_PRODUCT_TYPE: &str = "USDT-FUTURES";

#[tokio::test]
async fn bitget_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"])
    else {
        return Ok(());
    };
    let client = BitgetClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_spot_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Bitget, "bitget", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let uta = is_uta(&client).await;

    let method = if uta {
        "place_uta_order"
    } else {
        "place_spot_post_only_limit_buy_order"
    };
    let mut order_params = params(&[("product_symbol", BTC_USDT_SPOT), ("price", price.as_str())]);
    if uta {
        push(&mut order_params, "category", "SPOT");
        push(&mut order_params, "side", "buy");
        push(&mut order_params, "orderType", "limit");
        push(&mut order_params, "qty", quantity.clone());
        push(&mut order_params, "timeInForce", "post_only");
        push(&mut order_params, "clientOid", unique_client_id("dcexrs"));
    } else {
        push(&mut order_params, "size", quantity);
    }

    let order = match client.private_request(method, order_params).await {
        Ok(response) => response,
        Err(error) if bitget_unified_account_error(&error) => {
            eprintln!("skipping Bitget classic stateful order on unified account: {error}");
            return Ok(());
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_method = if uta {
        "cancel_uta_order"
    } else {
        "cancel_spot_order"
    };
    let mut cancel_params = params(&[("orderId", order_id.as_str())]);
    if uta {
        push(&mut cancel_params, "category", "SPOT");
    } else {
        push(&mut cancel_params, "product_symbol", BTC_USDT_SPOT);
    }
    let cancel = client.private_request(cancel_method, cancel_params).await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
async fn bitget_swap_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"])
    else {
        return Ok(());
    };
    let client = BitgetClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    let uta = is_uta(&client).await;

    if bitget_open_swap_orders(&client, uta).await? {
        eprintln!("skipping Bitget swap live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }
    if bitget_swap_position_abs(&client, uta).await? > 0.0 {
        eprintln!("skipping Bitget swap live stateful order; BTC-USDT swap position exists");
        return Ok(());
    }

    let orderbook = client
        .public_request(
            "get_futures_orderbook",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("limit", "5"),
            ]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Bitget, "bitget", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let transferred = match ensure_bitget_futures_margin(&client, uta).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order = bitget_place_swap_post_only_buy(&client, uta, &quantity, &price).await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel = bitget_cancel_swap_order(&client, uta, &order_id).await?;
    assert_success(&cancel);

    let opened = bitget_place_swap_market_buy(&client, uta, &quantity).await?;
    assert_success(&opened);
    assert!(wait_for_positive_position(|| bitget_swap_position_abs(&client, uta)).await? > 0.0);

    let closed = bitget_place_swap_market_sell_reduce_only(&client, uta, &quantity).await?;
    assert_success(&closed);
    assert_eq!(
        wait_for_flat_position(|| bitget_swap_position_abs(&client, uta)).await?,
        0.0
    );
    return_bitget_futures_margin(&client, uta, transferred).await?;
    Ok(())
}

async fn is_uta(client: &BitgetClient) -> bool {
    let Ok(response) = client
        .private_request("get_uta_account_info", Vec::new())
        .await
    else {
        return false;
    };
    response
        .data
        .get("data")
        .and_then(|data| data.get("permissions"))
        .and_then(Value::as_array)
        .is_some_and(|permissions| {
            permissions.iter().any(|permission| {
                matches!(permission.as_str(), Some("uta_trade") | Some("uta_mgt"))
            })
        })
}

async fn bitget_open_swap_orders(client: &BitgetClient, uta: bool) -> dcex::Result<bool> {
    let response = if uta {
        client
            .private_request(
                "get_uta_open_orders",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("limit", "20"),
                ]),
            )
            .await?
    } else {
        client
            .private_request(
                "get_futures_open_orders",
                params(&[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                    ("limit", "20"),
                ]),
            )
            .await?
    };
    Ok(contains_non_empty_array(
        &response.data,
        &["orderList", "orders", "list", "data"],
    ))
}

async fn bitget_swap_position_abs(client: &BitgetClient, uta: bool) -> dcex::Result<f64> {
    let response = if uta {
        client
            .private_request(
                "get_uta_positions",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("product_symbol", BTC_USDT_SWAP),
                ]),
            )
            .await?
    } else {
        client
            .private_request(
                "get_futures_positions",
                params(&[
                    ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                    ("marginCoin", "USDT"),
                ]),
            )
            .await?
    };
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["BTCUSDT", BTC_USDT_SWAP],
        &["total", "size", "qty"],
    ))
}

async fn ensure_bitget_futures_margin(
    client: &BitgetClient,
    uta: bool,
) -> dcex::Result<Option<f64>> {
    if bitget_futures_usdt(client, uta).await? >= 1.0 {
        return Ok(Some(0.0));
    }
    if uta {
        eprintln!("skipping Bitget UTA swap live stateful order; insufficient USDT");
        return Ok(None);
    }
    if bitget_spot_usdt(client).await? < 2.0 {
        eprintln!("skipping Bitget swap live stateful order; insufficient transferable USDT");
        return Ok(None);
    }
    let response = client
        .private_request(
            "transfer",
            params(&[
                ("coin", "USDT"),
                ("amount", "2"),
                ("fromType", "spot"),
                ("toType", "usdt_futures"),
                ("clientOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(2.0))
}

async fn return_bitget_futures_margin(
    client: &BitgetClient,
    uta: bool,
    amount: f64,
) -> dcex::Result<()> {
    if uta || amount <= 0.0 {
        return Ok(());
    }
    let available = bitget_futures_usdt(client, uta).await?;
    let amount = amount.min(available);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format!("{amount:.6}")
        .trim_end_matches('0')
        .trim_end_matches('.')
        .to_string();
    let response = client
        .private_request(
            "transfer",
            params(&[
                ("coin", "USDT"),
                ("amount", amount.as_str()),
                ("fromType", "usdt_futures"),
                ("toType", "spot"),
                ("clientOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await?;
    assert_success(&response);
    Ok(())
}

async fn bitget_spot_usdt(client: &BitgetClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_spot_account_assets", params(&[("coin", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available", "availableBalance"],
    ))
}

async fn bitget_futures_usdt(client: &BitgetClient, uta: bool) -> dcex::Result<f64> {
    let response = if uta {
        client
            .private_request("get_uta_account_assets", Vec::new())
            .await?
    } else {
        client
            .private_request(
                "get_futures_accounts",
                params(&[("productType", BITGET_FUTURES_PRODUCT_TYPE)]),
            )
            .await?
    };
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available", "availableBalance", "availableMargin"],
    ))
}

async fn bitget_place_swap_post_only_buy(
    client: &BitgetClient,
    uta: bool,
    quantity: &str,
    price: &str,
) -> dcex::Result<dcex::exchange::ValidatedResponse> {
    if uta {
        return client
            .private_request(
                "place_uta_order",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("side", "buy"),
                    ("orderType", "limit"),
                    ("qty", quantity),
                    ("price", price),
                    ("timeInForce", "post_only"),
                    ("marginMode", "crossed"),
                    ("clientOid", unique_client_id("dcexrs").as_str()),
                ]),
            )
            .await;
    }
    client
        .private_request(
            "place_futures_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("marginMode", "crossed"),
                ("marginCoin", "USDT"),
                ("size", quantity),
                ("price", price),
                ("clientOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await
}

async fn bitget_cancel_swap_order(
    client: &BitgetClient,
    uta: bool,
    order_id: &str,
) -> dcex::Result<dcex::exchange::ValidatedResponse> {
    if uta {
        return client
            .private_request(
                "cancel_uta_order",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("orderId", order_id),
                ]),
            )
            .await;
    }
    client
        .private_request(
            "cancel_futures_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("marginCoin", "USDT"),
                ("orderId", order_id),
            ]),
        )
        .await
}

async fn bitget_place_swap_market_buy(
    client: &BitgetClient,
    uta: bool,
    quantity: &str,
) -> dcex::Result<dcex::exchange::ValidatedResponse> {
    if uta {
        return client
            .private_request(
                "place_uta_order",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("side", "buy"),
                    ("orderType", "market"),
                    ("qty", quantity),
                    ("marginMode", "crossed"),
                    ("clientOid", unique_client_id("dcexrs").as_str()),
                ]),
            )
            .await;
    }
    client
        .private_request(
            "place_futures_market_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("marginMode", "crossed"),
                ("marginCoin", "USDT"),
                ("size", quantity),
                ("clientOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await
}

async fn bitget_place_swap_market_sell_reduce_only(
    client: &BitgetClient,
    uta: bool,
    quantity: &str,
) -> dcex::Result<dcex::exchange::ValidatedResponse> {
    if uta {
        return client
            .private_request(
                "place_uta_order",
                params(&[
                    ("category", BITGET_FUTURES_PRODUCT_TYPE),
                    ("product_symbol", BTC_USDT_SWAP),
                    ("side", "sell"),
                    ("orderType", "market"),
                    ("qty", quantity),
                    ("marginMode", "crossed"),
                    ("reduceOnly", "yes"),
                    ("clientOid", unique_client_id("dcexrs").as_str()),
                ]),
            )
            .await;
    }
    client
        .private_request(
            "place_futures_market_sell_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("marginMode", "crossed"),
                ("marginCoin", "USDT"),
                ("size", quantity),
                ("reduceOnly", "YES"),
                ("clientOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await
}
