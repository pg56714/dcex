use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::binance::BinanceClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, fetch_trading_details, format_transfer_amount,
    minimum_order_quantity, params, parse_positive, post_only_buy_price, require_env,
    require_live_trading, require_order_id, BTC_USDT_SPOT,
};

struct TransferBack {
    amount: String,
    transfer_type: &'static str,
}

#[tokio::test]
async fn binance_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BINANCE_API_KEY", "BINANCE_API_SECRET"]) else {
        return Ok(());
    };
    let client = BinanceClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_spot_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Binance, "binance", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")?;
    let transfer = match ensure_spot_usdt(&client, required_usdt * 1.01).await? {
        Some(transfer) => transfer,
        None if spot_usdt(&client).await? >= required_usdt => TransferBack {
            amount: "0".to_string(),
            transfer_type: "",
        },
        None => return Ok(()),
    };

    let order_result = client
        .private_request(
            "place_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("quantity", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_binance_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_result = client
        .private_request(
            "cancel_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("orderId", order_id.as_str()),
            ]),
        )
        .await;
    return_binance_transfer(&client, &transfer).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

async fn ensure_spot_usdt(
    client: &BinanceClient,
    required: f64,
) -> dcex::Result<Option<TransferBack>> {
    let spot = spot_usdt(client).await?;
    if spot >= required {
        return Ok(Some(TransferBack {
            amount: "0".to_string(),
            transfer_type: "",
        }));
    }
    let needed = required - spot;
    let sources = [
        (funding_usdt(client).await?, "FUNDING_MAIN", "MAIN_FUNDING"),
        (
            futures_usdt(client).await?,
            "UMFUTURE_MAIN",
            "MAIN_UMFUTURE",
        ),
    ];
    for (available, transfer_type, reverse_type) in sources {
        if available >= needed {
            let amount = format_transfer_amount(needed);
            let response = client
                .private_request(
                    "create_universal_transfer",
                    params(&[
                        ("type", transfer_type),
                        ("asset", "USDT"),
                        ("amount", amount.as_str()),
                    ]),
                )
                .await?;
            assert_success(&response);
            sleep(Duration::from_secs(1)).await;
            return Ok(Some(TransferBack {
                amount,
                transfer_type: reverse_type,
            }));
        }
    }
    eprintln!("skipping Binance live stateful order; insufficient transferable USDT");
    Ok(None)
}

async fn return_binance_transfer(
    client: &BinanceClient,
    transfer: &TransferBack,
) -> dcex::Result<()> {
    if transfer.amount == "0" {
        return Ok(());
    }
    let response = client
        .private_request(
            "create_universal_transfer",
            params(&[
                ("type", transfer.transfer_type),
                ("asset", "USDT"),
                ("amount", transfer.amount.as_str()),
            ]),
        )
        .await?;
    assert_success(&response);
    Ok(())
}

async fn spot_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_account_balance", params(&[("market_type", "spot")]))
        .await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn funding_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client
        .private_request(
            "get_funding_wallet",
            params(&[("asset", "USDT"), ("needBtcValuation", "false")]),
        )
        .await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn futures_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_account_balance", params(&[("market_type", "swap")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableBalance", "available", "free"],
    ))
}
