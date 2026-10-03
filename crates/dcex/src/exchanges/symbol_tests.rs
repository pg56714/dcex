//! Compact samples captured from official public instrument lists.

use serde_json::Value;

use crate::{DcexError, Result};

pub(super) fn table(
    exchange: &str,
    product: &str,
    native: &str,
) -> crate::product_table::ProductTable {
    use crate::product_table::{MarketInfo, ProductTable};
    ProductTable::new(vec![MarketInfo {
        exchange: exchange.into(),
        exchange_symbol: native.into(),
        product_symbol: product.into(),
        product_type: "swap".into(),
        exchange_type: "linear".into(),
        price_precision: "0.01".into(),
        size_precision: "1".into(),
        min_size: "1".into(),
        base_currency: product.split('-').next().unwrap().into(),
        quote_currency: "USD".into(),
        min_notional: "0".into(),
        size_per_contract: "1".into(),
    }])
}

pub(super) fn check(exchange: &str, convert: impl Fn(&str, &str) -> Result<String>) {
    let fixture: Value =
        serde_json::from_str(include_str!("../../tests/fixtures/symbol_fallback.json"))
            .expect("public symbol fixture");
    let rows = fixture["cases"].as_array().expect("cases");
    let mut count = 0;
    for row in rows.iter().filter(|row| row["exchange"] == exchange) {
        count += 1;
        let input = row["input"].as_str().expect("input");
        let result = convert(input, row["mode"].as_str().expect("mode"));
        if row["requires_table"] == true {
            assert!(
                matches!(&result, Err(DcexError::InvalidInput(message)) if message.contains("product table")),
                "{exchange} {input}: expected metadata requirement"
            );
        } else {
            assert_eq!(
                result.expect("symbol"),
                row["native"].as_str().expect("native"),
                "{exchange} {input}"
            );
        }
    }
    assert!(count > 0, "missing public samples for {exchange}");
}
