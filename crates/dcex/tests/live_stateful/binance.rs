use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::binance::BinanceClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    first_bid_price, format_transfer_amount, format_transfer_amount_floor,
    insufficient_funds_error, leveraged_margin_required, live_test_error, margin_target,
    minimum_order_quantity, parse_positive, post_only_buy_price_from_bid, price_below_market,
    require_env, require_live_trading, require_order_id, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

struct TransferBack {
    amount: String,
    transfer_type: &'static str,
}

const BINANCE_FUTURES_LEVERAGE: &str = "50";
const BINANCE_FUTURES_LEVERAGE_VALUE: f64 = 50.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
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

    let orderbook = client.get_spot_orderbook(BTC_USDT_SPOT).limit(5).await?;
    let details = fetch_trading_details(Exchange::Binance, "binance", BTC_USDT_SPOT).await?;
    let price = price_below_market(first_bid_price(&orderbook.data)?, &details, 0.95)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")?;
    let transfer = match ensure_spot_usdt(&client, required_usdt * 1.01).await? {
        Some(transfer) => transfer,
        None if spot_usdt(&client).await? >= required_usdt => TransferBack {
            amount: "0".to_string(),
            transfer_type: "",
        },
        None => {
            return Err(live_test_error(
                "Binance spot has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = client
        .place_post_only_limit_buy_order(BTC_USDT_SPOT, quantity.as_str(), price.as_str())
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
        .cancel_order(BTC_USDT_SPOT)
        .param("orderId", order_id.as_str())
        .await;
    return_binance_transfer(&client, &transfer).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn binance_futures_direct_live_stateful_order() -> dcex::Result<()> {
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
    cleanup_binance_futures_state(&client).await?;

    let ticker = client
        .get_futures_ticker()
        .param("product_symbol", BTC_USDT_SWAP)
        .await?;
    let details = fetch_trading_details(Exchange::Binance, "binance", BTC_USDT_SWAP).await?;
    let bid = find_f64(&ticker.data, &["bidPrice", "bid"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!("Binance futures ticker has no bid: {ticker:?}"))
    })?;
    let price = post_only_buy_price_from_bid(bid, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let leverage = client
        .set_leverage(BTC_USDT_SWAP, BINANCE_FUTURES_LEVERAGE)
        .await?;
    assert_success(&leverage);
    let required_usdt =
        leveraged_margin_required(bid, &quantity, &details, BINANCE_FUTURES_LEVERAGE_VALUE)?;
    let transfer = match ensure_futures_usdt(&client, margin_target(required_usdt)).await? {
        Some(transfer) => transfer,
        None => {
            return Err(live_test_error(
                "Binance futures has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = client
        .place_post_only_limit_buy_order(BTC_USDT_SWAP, quantity.as_str(), price.as_str())
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
        .cancel_order(BTC_USDT_SWAP)
        .param("orderId", order_id.as_str())
        .await;
    let cancel = match cancel_result {
        Ok(cancel) => cancel,
        Err(error) => {
            return_binance_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&cancel);

    let open_result = client
        .place_market_buy_order(BTC_USDT_SWAP, quantity.as_str())
        .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) if insufficient_funds_error(&error) => {
            return_binance_transfer(&client, &transfer).await?;
            return Err(live_test_error(format!(
                "Binance futures insufficient margin for market open: {error}"
            )));
        }
        Err(error) => {
            return_binance_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&opened);
    assert!(wait_for_positive_position(|| futures_position_abs(&client)).await? > 0.0);

    let closed = client
        .place_market_sell_order(BTC_USDT_SWAP, quantity.as_str())
        .param("reduceOnly", "true")
        .await?;
    assert_success(&closed);
    assert_eq!(
        wait_for_flat_position(|| futures_position_abs(&client)).await?,
        0.0
    );
    return_binance_transfer(&client, &transfer).await?;
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
                .create_universal_transfer(transfer_type, "USDT", amount.as_str())
                .await?;
            assert_success(&response);
            sleep(Duration::from_secs(1)).await;
            return Ok(Some(TransferBack {
                amount,
                transfer_type: reverse_type,
            }));
        }
    }
    Ok(None)
}

async fn ensure_futures_usdt(
    client: &BinanceClient,
    required: f64,
) -> dcex::Result<Option<TransferBack>> {
    let futures = futures_usdt(client).await?;
    if futures >= required {
        return Ok(Some(TransferBack {
            amount: "0".to_string(),
            transfer_type: "",
        }));
    }
    let needed = required - futures;
    let sources = [
        (
            funding_usdt(client).await?,
            "FUNDING_UMFUTURE",
            "UMFUTURE_FUNDING",
        ),
        (spot_usdt(client).await?, "MAIN_UMFUTURE", "UMFUTURE_MAIN"),
    ];
    for (available, transfer_type, reverse_type) in sources {
        if available >= needed {
            let amount = format_transfer_amount(needed);
            let response = client
                .create_universal_transfer(transfer_type, "USDT", amount.as_str())
                .await?;
            assert_success(&response);
            sleep(Duration::from_secs(1)).await;
            return Ok(Some(TransferBack {
                amount,
                transfer_type: reverse_type,
            }));
        }
    }
    Ok(None)
}

async fn cleanup_binance_futures_state(client: &BinanceClient) -> dcex::Result<()> {
    if binance_open_swap_orders(client).await? {
        let cancel = client.cancel_all_open_orders(BTC_USDT_SWAP).await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    let open_algo = client
        .get_all_open_futures_algo_orders()
        .param("product_symbol", BTC_USDT_SWAP)
        .await?;
    if contains_non_empty_array(&open_algo.data, &["orders", "data"]) {
        let cancel = client
            .cancel_all_open_futures_algo_orders(BTC_USDT_SWAP)
            .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }

    let amount = futures_position_amt(client).await?;
    if amount != 0.0 {
        let quantity = format_transfer_amount_floor(amount.abs(), 8);
        let close = client
            .place_market_order(
                BTC_USDT_SWAP,
                if amount > 0.0 { "SELL" } else { "BUY" },
                quantity.as_str(),
            )
            .param("reduceOnly", "true")
            .await?;
        assert_success(&close);
        sleep(Duration::from_secs(1)).await;
    }

    if binance_open_swap_orders(client).await? {
        return Err(live_test_error(
            "Binance futures still has open BTC-USDT swap orders after cleanup",
        ));
    }
    let open_algo = client
        .get_all_open_futures_algo_orders()
        .param("product_symbol", BTC_USDT_SWAP)
        .await?;
    if contains_non_empty_array(&open_algo.data, &["orders", "data"]) {
        return Err(live_test_error(
            "Binance futures still has open BTC-USDT algo orders after cleanup",
        ));
    }
    if wait_for_flat_position(|| futures_position_abs(client)).await? != 0.0 {
        return Err(live_test_error(
            "Binance futures BTC-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn return_binance_transfer(
    client: &BinanceClient,
    transfer: &TransferBack,
) -> dcex::Result<()> {
    if transfer.amount == "0" {
        return Ok(());
    }
    let requested = parse_positive(&transfer.amount, "transfer amount")?;
    let available = match transfer.transfer_type.split('_').next() {
        Some("FUNDING") => funding_usdt(client).await?,
        Some("MAIN") => spot_usdt(client).await?,
        Some("UMFUTURE") => futures_usdt(client).await?,
        _ => requested,
    };
    let amount = requested.min(available);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_floor(amount, 6);
    let response = client
        .create_universal_transfer(transfer.transfer_type, "USDT", amount.as_str())
        .await?;
    assert_success(&response);
    Ok(())
}

async fn spot_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client.get_account_balance("spot").await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn funding_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client
        .get_funding_wallet()
        .asset("USDT")
        .need_btc_valuation("false")
        .await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn futures_usdt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client.get_account_balance("swap").await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableBalance", "available", "free"],
    ))
}

async fn futures_position_abs(client: &BinanceClient) -> dcex::Result<f64> {
    Ok(futures_position_amt(client).await?.abs())
}

async fn futures_position_amt(client: &BinanceClient) -> dcex::Result<f64> {
    let response = client.get_future_position(BTC_USDT_SWAP).await?;
    Ok(find_f64(&response.data, &["positionAmt"]).unwrap_or(0.0))
}

async fn binance_open_swap_orders(client: &BinanceClient) -> dcex::Result<bool> {
    let response = client.get_open_orders(BTC_USDT_SWAP).await?;
    Ok(contains_non_empty_array(
        &response.data,
        &["data", "orders"],
    ))
}
