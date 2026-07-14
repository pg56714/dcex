use super::*;
use crate::product_table::MarketInfo;

#[test]
fn normalizes_exchange_specific_currency_aliases() {
    assert_eq!(normalize_kucoin_currency("XBT"), "BTC");
    assert_eq!(normalize_kraken_currency("XXBT"), "BTC");
    assert_eq!(normalize_kraken_currency("ZUSD"), "USD");
}

#[test]
fn preserves_python_precision_formatting() {
    assert_eq!(decimal_precision(3), "0.001");
    assert_eq!(decimal_precision(5), "1e-05");
    assert_eq!(decimal_precision(8), "1e-08");
    assert_eq!(python_float_string("10.00000000"), "10.0");
}

#[test]
fn builds_kraken_dated_inverse_product_symbol() {
    let market = serde_json::json!({"lastTradingTime": "2026-06-01"});
    assert_eq!(
        kraken_futures_product("FI_XBTUSD_260601", "BTC", "USD", "futures_inverse", &market,),
        (
            "BTC-USD-260601-INVERSE-SWAP".to_string(),
            "futures".to_string(),
        )
    );
}

#[test]
fn canonical_symbols_cover_exchange_specific_formats() {
    assert_eq!(
        binance_product_symbol("BTC", "USDT", "BTCUSDT", false),
        "BTC-USDT-SWAP"
    );
    assert_eq!(
        binance_product_symbol("BTC", "USDT", "BTCUSDT_260626", false),
        "BTC-USDT-260626-SWAP"
    );
    assert_eq!(binance_product_type("PERPETUAL"), "swap");
    assert_eq!(binance_product_type("CURRENT_QUARTER"), "futures");
    assert_eq!(
        bitmex_product_symbol("FFCCSX", "XBTUSDZ26", "XBT", "USD"),
        "XBT-USD-Z26-SWAP"
    );

    let mut inverse_base = "BTC".to_string();
    assert_eq!(
        bybit_product_symbol(
            "inverse",
            &mut inverse_base,
            "USD",
            "BTC-27MAR26",
            &["BTC", "27MAR26"],
        ),
        "BTC-USD-27MAR26-SWAP"
    );

    let mut inverse_base = "BTC".to_string();
    assert_eq!(
        bybit_product_symbol("inverse", &mut inverse_base, "USD", "BTCUSDH23", &[]),
        "BTC-USD-H23-SWAP"
    );
    assert_eq!(bybit_product_type("inverse", "InverseFutures"), "futures");
    assert_eq!(normalize_kucoin_currency("XBT"), "BTC");
    assert_eq!(normalize_kraken_currency("XXBT"), "BTC");
}

#[test]
fn product_table_indexes_non_text_exchange_symbols() {
    let table = crate::product_table::ProductTable::new(vec![
        MarketInfo {
            exchange: "hyperliquid".to_string(),
            exchange_symbol: "[\"BTC\", 0]".to_string(),
            product_symbol: "BTC-USD-SWAP".to_string(),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: "0.001".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0.001".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USD".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        },
        MarketInfo {
            exchange: "lighter".to_string(),
            exchange_symbol: "42".to_string(),
            product_symbol: "BTC-USDC-SWAP".to_string(),
            product_type: "swap".to_string(),
            exchange_type: "swap".to_string(),
            price_precision: "0.01".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USDC".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        },
    ]);

    assert_eq!(
        table
            .get_exchange_symbol("hyperliquid", "BTC-USD-SWAP")
            .expect("Hyperliquid asset mapping"),
        "[\"BTC\", 0]"
    );
    assert_eq!(
        table
            .get_exchange_symbol("lighter", "BTC-USDC-SWAP")
            .expect("Lighter market id"),
        "42"
    );
}
