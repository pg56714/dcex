use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitget::BitgetClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    account_restriction, assert_success, asset_amount, bitget_unified_account_error,
    contains_non_empty_array, fetch_trading_details, first_bid_price, format_transfer_amount,
    format_transfer_amount_floor, leveraged_margin_required, live_test_error, margin_target,
    minimum_order_quantity, params, post_only_buy_price, price_below_market, push, require_env,
    require_live_trading, require_order_id, sum_abs_values_for_symbols, unique_client_id,
    wait_for_flat_position, wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const BITGET_FUTURES_PRODUCT_TYPE: &str = "USDT-FUTURES";
const BITGET_SWAP_LEVERAGE: &str = "50";
const BITGET_SWAP_LEVERAGE_VALUE: f64 = 50.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
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

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Bitget, "bitget", BTC_USDT_SPOT).await?;
    let price = price_below_market(first_bid_price(&orderbook.data)?, &details, 0.95)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let uta = is_uta(&client).await;

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

    let order_result = if uta {
        super::common::exchange_method_request(&client, "place_uta_order", order_params).await
    } else {
        super::common::exchange_method_request(
            &client,
            "place_spot_post_only_limit_buy_order",
            order_params,
        )
        .await
    };
    let order = match order_result {
        Ok(response) => response,
        Err(error) if bitget_unified_account_error(&error) => {
            return Err(live_test_error(format!(
                "Bitget classic stateful order is unsupported on unified account: {error}"
            )));
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let mut cancel_params = params(&[("orderId", order_id.as_str())]);
    if uta {
        push(&mut cancel_params, "category", "SPOT");
    } else {
        push(&mut cancel_params, "product_symbol", BTC_USDT_SPOT);
    }
    let cancel_result = if uta {
        super::common::exchange_method_request(&client, "cancel_uta_order", cancel_params).await
    } else {
        super::common::exchange_method_request(&client, "cancel_spot_order", cancel_params).await
    };
    match cancel_result {
        Ok(cancel) => assert_success(&cancel),
        Err(error)
            if account_restriction(
                &error,
                &["order does not exist", "25204", "does not exist"],
            ) =>
        {
            if bitget_open_spot_orders(&client, uta).await? {
                return Err(error);
            }
            eprintln!("Bitget spot post-only order was already absent before cancel");
        }
        Err(error) => return Err(error),
    }
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
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

    cleanup_bitget_swap_state(&client, uta).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
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
    set_bitget_swap_leverage(&client, uta).await?;
    let market_price_estimate = first_bid_price(&orderbook.data)?;
    let required_usdt = leveraged_margin_required(
        market_price_estimate,
        &quantity,
        &details,
        BITGET_SWAP_LEVERAGE_VALUE,
    )?;
    let transferred =
        match ensure_bitget_futures_margin(&client, uta, margin_target(required_usdt)).await? {
            Some(amount) => amount,
            None => {
                return Err(live_test_error(
                    "Bitget swap has insufficient transferable USDT for live stateful order",
                ));
            }
        };

    let order_result = bitget_place_swap_post_only_buy(&client, uta, &quantity, &price).await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_bitget_futures_margin(&client, uta, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel_result = bitget_cancel_swap_order(&client, uta, &order_id).await;
    let cancel = match cancel_result {
        Ok(cancel) => cancel,
        Err(error) => {
            return_bitget_futures_margin(&client, uta, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&cancel);

    let open_result = bitget_place_swap_market_buy(&client, uta, &quantity).await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) => {
            return_bitget_futures_margin(&client, uta, transferred).await?;
            return Err(error);
        }
    };
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
    let Ok(response) = client.get_uta_account_info().await else {
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
        super::common::exchange_method_request(
            &client,
            "get_uta_open_orders",
            params(&[
                ("category", BITGET_FUTURES_PRODUCT_TYPE),
                ("product_symbol", BTC_USDT_SWAP),
                ("limit", "20"),
            ]),
        )
        .await?
    } else {
        super::common::exchange_method_request(
            &client,
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

async fn bitget_open_spot_orders(client: &BitgetClient, uta: bool) -> dcex::Result<bool> {
    let response = if uta {
        super::common::exchange_method_request(
            &client,
            "get_uta_open_orders",
            params(&[
                ("category", "SPOT"),
                ("product_symbol", BTC_USDT_SPOT),
                ("limit", "20"),
            ]),
        )
        .await?
    } else {
        super::common::exchange_method_request(
            &client,
            "get_spot_open_orders",
            params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "20")]),
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
        super::common::exchange_method_request(
            &client,
            "get_uta_positions",
            params(&[
                ("category", BITGET_FUTURES_PRODUCT_TYPE),
                ("product_symbol", BTC_USDT_SWAP),
            ]),
        )
        .await?
    } else {
        super::common::exchange_method_request(
            &client,
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

async fn cleanup_bitget_swap_state(client: &BitgetClient, uta: bool) -> dcex::Result<()> {
    if bitget_open_swap_orders(client, uta).await? {
        return Err(live_test_error(
            "Bitget swap has open BTC-USDT orders before live stateful order",
        ));
    }
    let position = bitget_swap_position_abs(client, uta).await?;
    if position > 0.0 {
        let quantity = format_transfer_amount_floor(position, 8);
        let close = bitget_place_swap_market_sell_reduce_only(client, uta, &quantity).await?;
        assert_success(&close);
        sleep(Duration::from_secs(2)).await;
    }
    if wait_for_flat_position(|| bitget_swap_position_abs(client, uta)).await? != 0.0 {
        return Err(live_test_error(
            "Bitget BTC-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn ensure_bitget_futures_margin(
    client: &BitgetClient,
    uta: bool,
    required: f64,
) -> dcex::Result<Option<f64>> {
    let futures = bitget_futures_usdt(client, uta).await?;
    if futures >= required {
        return Ok(Some(0.0));
    }
    let needed = required - futures;
    if uta {
        return Ok(None);
    }
    let spot = bitget_spot_usdt(client).await?;
    if spot < needed {
        return Ok(None);
    }
    let amount = format_transfer_amount(needed);
    let response = super::common::exchange_method_request(
        &client,
        "transfer",
        params(&[
            ("coin", "USDT"),
            ("amount", amount.as_str()),
            ("fromType", "spot"),
            ("toType", "usdt_futures"),
            ("clientOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
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
    let amount = format_transfer_amount_floor(amount, 6);
    let response = super::common::exchange_method_request(
        &client,
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
    let response = super::common::exchange_method_request(
        &client,
        "get_spot_account_assets",
        params(&[("coin", "USDT")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available", "availableBalance"],
    ))
}

async fn bitget_futures_usdt(client: &BitgetClient, uta: bool) -> dcex::Result<f64> {
    let response = if uta {
        client.get_uta_account_assets().await?
    } else {
        super::common::exchange_method_request(
            &client,
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
        return super::common::exchange_method_request(
            &client,
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
    super::common::exchange_method_request(
        &client,
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

async fn set_bitget_swap_leverage(client: &BitgetClient, uta: bool) -> dcex::Result<()> {
    let result = if uta {
        super::common::exchange_method_request(
            &client,
            "set_uta_leverage",
            params(&[
                ("category", BITGET_FUTURES_PRODUCT_TYPE),
                ("product_symbol", BTC_USDT_SWAP),
                ("leverage", BITGET_SWAP_LEVERAGE),
                ("marginMode", "crossed"),
            ]),
        )
        .await
    } else {
        super::common::exchange_method_request(
            &client,
            "set_futures_leverage",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("productType", BITGET_FUTURES_PRODUCT_TYPE),
                ("marginCoin", "USDT"),
                ("leverage", BITGET_SWAP_LEVERAGE),
            ]),
        )
        .await
    };
    match result {
        Ok(response) => {
            assert_success(&response);
            Ok(())
        }
        Err(error) if error.to_string().contains("leverage is the same") => Ok(()),
        Err(error) => Err(error),
    }
}

async fn bitget_cancel_swap_order(
    client: &BitgetClient,
    uta: bool,
    order_id: &str,
) -> dcex::Result<dcex::exchange::ValidatedResponse> {
    if uta {
        return super::common::exchange_method_request(
            &client,
            "cancel_uta_order",
            params(&[
                ("category", BITGET_FUTURES_PRODUCT_TYPE),
                ("orderId", order_id),
            ]),
        )
        .await;
    }
    super::common::exchange_method_request(
        &client,
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
        return super::common::exchange_method_request(
            &client,
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
    super::common::exchange_method_request(
        &client,
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
        return super::common::exchange_method_request(
            &client,
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
    super::common::exchange_method_request(
        &client,
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
