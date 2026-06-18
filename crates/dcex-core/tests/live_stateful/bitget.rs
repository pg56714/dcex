use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitget::BitgetClient;
use serde_json::Value;

use super::common::{
    assert_success, bitget_unified_account_error, fetch_trading_details, minimum_order_quantity,
    params, post_only_buy_price, push, require_env, require_live_trading, require_order_id,
    unique_client_id, BTC_USDT_SPOT,
};

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
