use std::collections::HashMap;
use std::time::Duration;

use serde_json::Value;

use crate::exchanges::aster::AsterClient;
use crate::exchanges::backpack::BackpackClient;
use crate::exchanges::binance::BinanceClient;
use crate::exchanges::bingx::BingxClient;
use crate::exchanges::bitget::BitgetClient;
use crate::exchanges::bitmex::BitmexClient;
use crate::exchanges::bybit::BybitClient;
use crate::exchanges::extended::ExtendedClient;
use crate::exchanges::hyperliquid::HyperliquidClient;
use crate::exchanges::kraken::KrakenClient;
use crate::exchanges::kucoin::KucoinClient;
use crate::exchanges::lighter::LighterClient;
use crate::exchanges::mexc::MexcClient;
use crate::exchanges::okx::OkxClient;
use crate::product_table::MarketInfo;
use crate::Result;

use super::*;
pub(super) async fn fetch_aster(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = AsterClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_exchange_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        if value_string(market, "status", "") == "TRADING" {
            rows.push(aster_market_info(market, "spot")?);
        }
    }
    for market in response_array(&futures, &["symbols"]) {
        if value_string(market, "status", "") != "TRADING" {
            continue;
        }
        let product_type = if value_string(market, "contractType", "") == "PERPETUAL" {
            "swap"
        } else {
            "futures"
        };
        rows.push(aster_market_info(market, product_type)?);
    }
    Ok(rows)
}

fn aster_market_info(market: &Value, product_type: &str) -> Result<MarketInfo> {
    let symbol = required_string(market, "symbol")?;
    let base = required_string(market, "baseAsset")?;
    let quote = required_string(market, "quoteAsset")?;
    let filters = value_array(market.get("filters"));
    let price = find_filter(filters, &["PRICE_FILTER"]);
    let lot = find_filter(filters, &["LOT_SIZE"]);
    let notional = find_filter(filters, &["MIN_NOTIONAL", "NOTIONAL"]);
    Ok(MarketInfo {
        exchange: "aster".to_string(),
        exchange_symbol: symbol,
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: if product_type == "spot" {
            "spot".to_string()
        } else {
            value_string(market, "contractType", "PERPETUAL")
        },
        price_precision: value_string(price, "tickSize", "0"),
        size_precision: value_string(lot, "stepSize", "0"),
        min_size: value_string(lot, "minQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: first_non_empty(
            value_string(notional, "minNotional", ""),
            value_string(notional, "notional", "0"),
        ),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_backpack(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BackpackClient::public(5_000, timeout)?;
    let response = client.public_request("get_markets", vec![]).await?;
    let mut rows = Vec::new();
    for market in value_array(Some(&response.data)) {
        if market.get("visible").and_then(Value::as_bool) == Some(false)
            || !value_string(market, "orderBookState", "").eq_ignore_ascii_case("open")
        {
            continue;
        }
        let market_type = value_string(market, "marketType", "").to_ascii_uppercase();
        if !matches!(market_type.as_str(), "SPOT" | "PERP" | "IPERP" | "DATED") {
            continue;
        }
        let symbol = required_string(market, "symbol")?;
        let base = non_empty_string(market, "baseSymbol")
            .unwrap_or_else(|| symbol.split('_').next().unwrap_or(&symbol).to_string());
        let quote = non_empty_string(market, "quoteSymbol").unwrap_or_else(|| "USDC".to_string());
        let product_type = match market_type.as_str() {
            "SPOT" => "spot",
            "PERP" | "IPERP" => "swap",
            "DATED" => "futures",
            _ => unreachable!(),
        };
        let filters = market.get("filters").and_then(Value::as_object);
        let price = filters
            .and_then(|filters| filters.get("price"))
            .unwrap_or(&Value::Null);
        let quantity = filters
            .and_then(|filters| filters.get("quantity"))
            .unwrap_or(&Value::Null);
        rows.push(MarketInfo {
            exchange: "backpack".to_string(),
            exchange_symbol: symbol,
            product_symbol: if product_type == "swap" {
                format!("{base}-{quote}-SWAP")
            } else {
                format!("{base}-{quote}-{}", product_type.to_ascii_uppercase())
            },
            product_type: product_type.to_string(),
            exchange_type: market_type,
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(quantity, "stepSize", "0"),
            min_size: value_string(quantity, "minQuantity", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_binance(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BinanceClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_exchange_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        let base = required_string(market, "baseAsset")?;
        let quote = required_string(market, "quoteAsset")?;
        let filters = value_array(market.get("filters"));
        let price = find_filter(filters, &["PRICE_FILTER"]);
        let lot = find_filter(filters, &["LOT_SIZE"]);
        let notional = find_filter(filters, &["NOTIONAL"]);
        rows.push(MarketInfo {
            exchange: "binance".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(lot, "stepSize", "0"),
            min_size: value_string(lot, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: python_float_string(&value_string(notional, "minNotional", "0")),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["symbols"]) {
        let base = required_string(market, "baseAsset")?;
        let quote = required_string(market, "quoteAsset")?;
        let symbol = required_string(market, "symbol")?;
        let product_symbol = binance_product_symbol(&base, &quote, &symbol, false);
        let filters = value_array(market.get("filters"));
        let price = find_filter(filters, &["PRICE_FILTER"]);
        let lot = find_filter(filters, &["LOT_SIZE"]);
        let notional = find_filter(filters, &["MIN_NOTIONAL"]);
        rows.push(MarketInfo {
            exchange: "binance".to_string(),
            exchange_symbol: symbol,
            product_symbol,
            product_type: "swap".to_string(),
            exchange_type: value_string(market, "contractType", ""),
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(lot, "stepSize", "0"),
            min_size: value_string(lot, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(notional, "notional", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_bingx(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BingxClient::public(timeout)?;
    let swap = client
        .public_request("get_swap_instrument_info", vec![])
        .await?;
    let spot = client
        .public_request("get_spot_instrument_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&swap, &["data"]) {
        let symbol = required_string(market, "symbol")?;
        let (base, quote) = split_last(&symbol, '-')?;
        let price_places = value_i32(market, "pricePrecision", 0);
        let quantity_places = value_i32(market, "quantityPrecision", 0);
        rows.push(MarketInfo {
            exchange: "bingx".to_string(),
            exchange_symbol: symbol,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: decimal_precision_or_zero(price_places),
            size_precision: decimal_precision_or_zero(quantity_places),
            min_size: decimal_precision_or_zero(quantity_places),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "tradeMinUSDT", "0"),
            size_per_contract: value_string(market, "size", "1"),
        });
    }
    let spot_data = spot.data.get("data").unwrap_or(&Value::Null);
    let spot_symbols = spot_data.get("symbols").unwrap_or(spot_data);
    for market in value_array(Some(spot_symbols)) {
        let symbol = required_string(market, "symbol")?;
        let (base, quote) = split_last(&symbol, '-')?;
        rows.push(MarketInfo {
            exchange: "bingx".to_string(),
            exchange_symbol: symbol,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: value_string(market, "stepSize", "0"),
            min_size: value_string(market, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minNotional", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_bitget(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BitgetClient::public(timeout)?;
    let spot = client.public_request("get_spot_symbols", vec![]).await?;
    let futures = client
        .public_request(
            "get_futures_contracts",
            vec![("productType".to_string(), "USDT-FUTURES".to_string())],
        )
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["data"]) {
        let status = value_string(market, "status", "").to_ascii_lowercase();
        if !status.is_empty() && status != "online" {
            continue;
        }
        let base = required_string(market, "baseCoin")?;
        let quote = required_string(market, "quoteCoin")?;
        rows.push(MarketInfo {
            exchange: "bitget".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: decimal_precision(value_i32(market, "pricePrecision", 0)),
            size_precision: decimal_precision(value_i32(market, "quantityPrecision", 0)),
            min_size: value_string(market, "minTradeAmount", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minTradeUSDT", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["data"]) {
        let status = first_non_empty(
            value_string(market, "symbolStatus", ""),
            value_string(market, "status", ""),
        )
        .to_ascii_lowercase();
        if !status.is_empty() && !matches!(status.as_str(), "normal" | "online") {
            continue;
        }
        let base = required_string(market, "baseCoin")?;
        let quote = required_string(market, "quoteCoin")?;
        rows.push(MarketInfo {
            exchange: "bitget".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: value_string(market, "symbolType", "USDT-FUTURES"),
            price_precision: decimal_precision(value_i32(market, "pricePlace", 0)),
            size_precision: decimal_precision(value_i32(market, "volumePlace", 0)),
            min_size: value_string(market, "minTradeNum", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minTradeUSDT", "0"),
            size_per_contract: value_string(market, "sizeMultiplier", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_bitmex(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BitmexClient::public(timeout)?;
    let response = client
        .public_request(
            "get_instrument_info",
            vec![
                (
                    "filter".to_string(),
                    r#"{"typ":["FFWCSX","FFCCSX","IFXXXP"]}"#.to_string(),
                ),
                ("count".to_string(), "500".to_string()),
            ],
        )
        .await?;
    let mut rows = Vec::new();
    for market in value_array(Some(&response.data)) {
        let typ = value_string(market, "typ", "");
        let product_type = match typ.as_str() {
            "FFWCSX" => "swap",
            "FFCCSX" => "futures",
            "IFXXXP" => "spot",
            _ => continue,
        };
        let symbol = required_string(market, "symbol")?;
        let base = value_string(market, "underlying", "");
        let quote = required_string(market, "quoteCurrency")?;
        let product_symbol = bitmex_product_symbol(&typ, &symbol, &base, &quote);
        rows.push(MarketInfo {
            exchange: "bitmex".to_string(),
            exchange_symbol: symbol,
            product_symbol,
            product_type: product_type.to_string(),
            exchange_type: typ,
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: value_string(market, "lotSize", "0"),
            min_size: value_string(market, "lotSize", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: value_string(market, "multiplier", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_bybit(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BybitClient::public(5_000, false, timeout)?;
    let mut rows = Vec::new();
    for category in ["linear", "inverse", "spot"] {
        let markets = bybit_instruments(&client, category).await?;
        for market in markets {
            let mut base = required_string(&market, "baseCoin")?;
            let quote = required_string(&market, "quoteCoin")?;
            let symbol = required_string(&market, "symbol")?;
            let parts = symbol.split('-').collect::<Vec<_>>();
            let product_symbol = bybit_product_symbol(category, &mut base, &quote, &symbol, &parts);
            let product_type = if category == "spot" {
                "spot"
            } else if value_string(&market, "contractType", "") == "LinearFutures" {
                "futures"
            } else {
                "swap"
            };
            let price = market.get("priceFilter").unwrap_or(&Value::Null);
            let lot = market.get("lotSizeFilter").unwrap_or(&Value::Null);
            rows.push(MarketInfo {
                exchange: "bybit".to_string(),
                exchange_symbol: symbol,
                product_symbol,
                product_type: product_type.to_string(),
                exchange_type: category.to_string(),
                price_precision: value_string(price, "tickSize", "0"),
                size_precision: value_string(
                    lot,
                    if category == "spot" {
                        "basePrecision"
                    } else {
                        "qtyStep"
                    },
                    "0",
                ),
                min_size: value_string(lot, "minOrderQty", "0"),
                base_currency: base,
                quote_currency: quote,
                min_notional: if category == "spot" {
                    value_string(lot, "minOrderAmt", "0")
                } else if category == "inverse" {
                    "0".to_string()
                } else {
                    value_string(lot, "minNotionalValue", "0")
                },
                size_per_contract: "1".to_string(),
            });
        }
    }
    Ok(rows)
}

async fn bybit_instruments(client: &BybitClient, category: &str) -> Result<Vec<Value>> {
    let mut rows = Vec::new();
    let mut cursor: Option<String> = None;
    loop {
        let mut params = vec![("category".to_string(), category.to_string())];
        if let Some(cursor) = cursor.as_ref() {
            params.push(("cursor".to_string(), cursor.clone()));
        }
        let response = client
            .public_request("get_instruments_info", params)
            .await?;
        let result = response.data.get("result").unwrap_or(&Value::Null);
        rows.extend(value_array(result.get("list")).iter().cloned());
        let next = value_string(result, "nextPageCursor", "");
        if next.is_empty() {
            break;
        }
        cursor = Some(next);
    }
    Ok(rows)
}

pub(super) async fn fetch_extended(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = ExtendedClient::public(timeout)?;
    let response = client.public_request("get_markets", vec![]).await?;
    let mut rows = Vec::new();
    for market in response_array(&response, &["data"]) {
        if market.get("active").and_then(Value::as_bool) == Some(false) {
            continue;
        }
        let status = value_string(market, "status", "");
        if status != "ACTIVE" {
            continue;
        }
        rows.push(extended_market_info(market)?);
    }
    Ok(rows)
}

fn extended_market_info(market: &Value) -> Result<MarketInfo> {
    let symbol = required_string(market, "name")?;
    let market_type = value_string(market, "type", "PERPETUAL");
    let base = required_string(market, "assetName")?;
    let quote = required_string(market, "collateralAssetName")?;
    let config = market.get("tradingConfig").unwrap_or(&Value::Null);
    let product_type = if market_type == "SPOT" {
        "spot"
    } else {
        "swap"
    };
    Ok(MarketInfo {
        exchange: "extended".to_string(),
        exchange_symbol: symbol,
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: market_type,
        price_precision: value_string(config, "minPriceChange", "0"),
        size_precision: value_string(config, "minOrderSizeChange", "0"),
        min_size: value_string(config, "minOrderSize", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_hyperliquid(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = HyperliquidClient::public(false, timeout)?;
    let perpetual = client.public_request("get_meta", Vec::new()).await?;
    let spot = client.public_request("get_spot_meta", Vec::new()).await?;
    let mut rows = Vec::new();
    for (index, market) in response_array(&perpetual, &["universe"]).iter().enumerate() {
        let coin = required_string(market, "name")?;
        let precision = decimal_precision(value_i32(market, "szDecimals", 0));
        rows.push(MarketInfo {
            exchange: "hyperliquid".to_string(),
            exchange_symbol: format!("[\"{coin}\", {index}]"),
            product_symbol: format!("{coin}-USD-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: precision.clone(),
            size_precision: precision.clone(),
            min_size: precision,
            base_currency: coin,
            quote_currency: "USD".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    let mut tokens = HashMap::new();
    for token in response_array(&spot, &["tokens"]) {
        if let Some(index) = token.get("index").and_then(Value::as_i64) {
            tokens.insert(index, token);
        }
    }
    for (index, market) in response_array(&spot, &["universe"]).iter().enumerate() {
        let token_indexes = value_array(market.get("tokens"));
        if token_indexes.len() < 2 {
            continue;
        }
        let Some(base_token) = token_indexes[0]
            .as_i64()
            .and_then(|value| tokens.get(&value))
        else {
            continue;
        };
        let Some(quote_token) = token_indexes[1]
            .as_i64()
            .and_then(|value| tokens.get(&value))
        else {
            continue;
        };
        let base = required_string(base_token, "name")?;
        let quote = required_string(quote_token, "name")?;
        let precision = decimal_precision(value_i32(base_token, "szDecimals", 0));
        let asset_index = market
            .get("index")
            .and_then(Value::as_u64)
            .unwrap_or(index as u64);
        rows.push(MarketInfo {
            exchange: "hyperliquid".to_string(),
            exchange_symbol: format!(
                "[\"{}\", {}]",
                required_string(market, "name")?,
                10_000 + asset_index
            ),
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: precision.clone(),
            size_precision: precision.clone(),
            min_size: precision,
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_kucoin(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = KucoinClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_instrument_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_contracts", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["data"]) {
        let base = required_string(market, "baseCurrency")?;
        let quote = required_string(market, "quoteCurrency")?;
        rows.push(MarketInfo {
            exchange: "kucoin".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(market, "priceIncrement", "0"),
            size_precision: value_string(market, "baseIncrement", "0"),
            min_size: value_string(market, "baseMinSize", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: non_empty_string(market, "minFunds").unwrap_or_else(|| "0".to_string()),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["data"]) {
        let base = normalize_kucoin_currency(&required_string(market, "baseCurrency")?);
        let quote = required_string(market, "quoteCurrency")?;
        rows.push(MarketInfo {
            exchange: "kucoin".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: value_string(market, "type", ""),
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: value_string(market, "lotSize", "0"),
            min_size: value_string(market, "lotSize", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: value_string(market, "multiplier", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_kraken(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = KrakenClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_asset_pairs", vec![])
        .await?;
    let futures = client
        .public_request(
            "get_futures_instruments",
            vec![
                ("contractType".to_string(), "futures_inverse".to_string()),
                ("contractType".to_string(), "futures_vanilla".to_string()),
                ("contractType".to_string(), "flexible_futures".to_string()),
            ],
        )
        .await?;
    let mut rows = Vec::new();
    if let Some(result) = spot.data.get("result").and_then(Value::as_object) {
        for (symbol, market) in result {
            let status = value_string(market, "status", "");
            if !status.is_empty() && status != "online" {
                continue;
            }
            let wsname = value_string(market, "wsname", "");
            let (base, quote) = if let Some((base, quote)) = wsname.split_once('/') {
                (
                    normalize_kraken_currency(base),
                    normalize_kraken_currency(quote),
                )
            } else {
                (
                    normalize_kraken_currency(&value_string(market, "base", "")),
                    normalize_kraken_currency(&value_string(market, "quote", "")),
                )
            };
            rows.push(MarketInfo {
                exchange: "kraken".to_string(),
                exchange_symbol: symbol.clone(),
                product_symbol: format!("{base}-{quote}-SPOT"),
                product_type: "spot".to_string(),
                exchange_type: "spot".to_string(),
                price_precision: market.get("tick_size").map_or_else(
                    || decimal_precision(value_i32(market, "pair_decimals", 0)),
                    json_string,
                ),
                size_precision: decimal_precision(value_i32(market, "lot_decimals", 0)),
                min_size: value_string(market, "ordermin", "0"),
                base_currency: base,
                quote_currency: quote,
                min_notional: value_string(market, "costmin", "0"),
                size_per_contract: "1".to_string(),
            });
        }
    }
    for market in response_array(&futures, &["instruments"]) {
        let instrument_type = value_string(market, "type", "");
        if instrument_type == "options"
            || market.get("tradeable").and_then(Value::as_bool) != Some(true)
            || market
                .get("isExpired")
                .and_then(Value::as_bool)
                .unwrap_or(false)
        {
            continue;
        }
        let symbol = required_string(market, "symbol")?;
        let base = normalize_kraken_currency(&value_string(market, "base", ""));
        let quote = normalize_kraken_currency(&value_string(market, "quote", ""));
        let (product_symbol, product_type) =
            kraken_futures_product(&symbol, &base, &quote, &instrument_type, market);
        let precision = kraken_size_precision(market);
        rows.push(MarketInfo {
            exchange: "kraken".to_string(),
            exchange_symbol: symbol,
            product_symbol,
            product_type,
            exchange_type: instrument_type,
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: precision.clone(),
            min_size: precision,
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: value_string(market, "contractSize", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_lighter(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = LighterClient::new(timeout)?;
    let response = client
        .public_request("get_order_book_details", Vec::new())
        .await?;
    let mut rows = Vec::new();
    for (key, product_type) in [
        ("order_book_details", "swap"),
        ("spot_order_book_details", "spot"),
    ] {
        for market in response_array(&response, &[key]) {
            if !value_string(market, "status", "").eq_ignore_ascii_case("active") {
                continue;
            }
            rows.push(lighter_market_info(market, product_type)?);
        }
    }
    Ok(rows)
}

fn lighter_market_info(market: &Value, product_type: &str) -> Result<MarketInfo> {
    let symbol = required_string(market, "symbol")?;
    let (base, quote) = if product_type == "spot" {
        symbol.split_once('/').map_or_else(
            || (symbol.clone(), "USDC".to_string()),
            |(base, quote)| (base.to_string(), quote.to_string()),
        )
    } else {
        (symbol, "USDC".to_string())
    };
    Ok(MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: value_string(market, "market_id", ""),
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: non_empty_string(market, "market_type")
            .unwrap_or_else(|| product_type.to_string()),
        price_precision: lighter_precision(market, "price_decimals", "supported_price_decimals"),
        size_precision: lighter_precision(market, "size_decimals", "supported_size_decimals"),
        min_size: value_string(market, "min_base_amount", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: value_string(market, "min_quote_amount", "0"),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_mexc(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = MexcClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let contracts = client
        .public_request("get_contract_details", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        let status = value_string(market, "status", "");
        if (!status.is_empty() && !matches!(status.as_str(), "1" | "TRADING"))
            || market.get("isSpotTradingAllowed").and_then(Value::as_bool) == Some(false)
        {
            continue;
        }
        let base = required_string(market, "baseAsset")?;
        let quote = required_string(market, "quoteAsset")?;
        rows.push(MarketInfo {
            exchange: "mexc".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: decimal_precision(value_i32(market, "quotePrecision", 0)),
            size_precision: value_string(market, "baseSizePrecision", "0"),
            min_size: value_string(market, "baseSizePrecision", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "quoteAmountPrecision", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    let contract_data = contracts.data.get("data").unwrap_or(&Value::Null);
    let contract_rows = if contract_data.is_object() {
        vec![contract_data]
    } else {
        value_array(Some(contract_data)).iter().collect()
    };
    for market in contract_rows {
        let state = market.get("state");
        if state.is_some_and(|value| {
            !value.is_null() && value.as_i64() != Some(0) && value.as_str() != Some("0")
        }) || market.get("apiAllowed").and_then(Value::as_bool) == Some(false)
        {
            continue;
        }
        let base = required_string(market, "baseCoin")?;
        let quote = required_string(market, "quoteCoin")?;
        rows.push(MarketInfo {
            exchange: "mexc".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: value_string(market, "priceUnit", "0"),
            size_precision: value_string(market, "volUnit", "0"),
            min_size: value_string(market, "minVol", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: value_string(market, "contractSize", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_okx(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = OkxClient::public(timeout)?;
    let mut rows = Vec::new();
    for (instrument_type, product_type) in
        [("SWAP", "swap"), ("SPOT", "spot"), ("FUTURES", "futures")]
    {
        let response = client
            .public_request(
                "get_public_instruments",
                vec![("instType".to_string(), instrument_type.to_string())],
            )
            .await?;
        for market in response_array(&response, &["data"]) {
            let exchange_symbol = required_string(market, "instId")?;
            let parts = exchange_symbol.split('-').collect::<Vec<_>>();
            if parts.len() < 2 {
                continue;
            }
            let base = if product_type == "spot" {
                required_string(market, "baseCcy")?
            } else {
                parts[0].to_string()
            };
            let quote = if product_type == "spot" {
                required_string(market, "quoteCcy")?
            } else {
                parts[1].to_string()
            };
            rows.push(MarketInfo {
                exchange: "okx".to_string(),
                product_symbol: if product_type == "spot" {
                    format!("{exchange_symbol}-SPOT")
                } else {
                    exchange_symbol.clone()
                },
                exchange_symbol,
                product_type: product_type.to_string(),
                exchange_type: value_string(market, "instType", ""),
                price_precision: value_string(market, "tickSz", "0"),
                size_precision: value_string(market, "lotSz", "0"),
                min_size: value_string(market, "minSz", "0"),
                base_currency: base,
                quote_currency: quote,
                min_notional: "0".to_string(),
                size_per_contract: if product_type == "swap" {
                    value_string(market, "ctVal", "1")
                } else {
                    "1".to_string()
                },
            });
        }
    }
    Ok(rows)
}
