use crate::{DcexError, Result};

mod private;
mod public;

pub use private::BitmexPrivateWebSocket;
pub use public::BitmexPublicWebSocket;

const NO_SYMBOL_TABLES: &[&str] = &[
    "account",
    "affiliate",
    "announcement",
    "connected",
    "chat",
    "insurance",
    "margin",
    "publicNotifications",
    "privateNotifications",
    "transact",
    "wallet",
];

pub(super) fn subscription_arg(table: &str, product_symbol: Option<&str>) -> Result<String> {
    let table = normalize_table(table)?;
    if NO_SYMBOL_TABLES.contains(&table.as_str()) {
        return Ok(table);
    }
    let product_symbol = product_symbol.ok_or_else(|| {
        DcexError::InvalidInput(format!("BitMEX table {table} requires a symbol."))
    })?;
    let symbol = normalize_symbol(product_symbol)?;
    Ok(format!("{table}:{symbol}"))
}

pub(super) fn normalize_subscription_arg(arg: &str) -> Result<String> {
    let arg = arg.trim();
    if arg.is_empty() {
        return Err(DcexError::InvalidInput(
            "BitMEX WebSocket subscription must not be empty.".to_string(),
        ));
    }
    if !arg
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, ':' | '_' | '.'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX WebSocket subscription: {arg}"
        )));
    }
    Ok(arg.to_string())
}

pub(super) fn normalize_symbol(product_symbol: &str) -> Result<String> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "BitMEX WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if product_symbol.contains('-') {
        let parts = product_symbol.split('-').collect::<Vec<_>>();
        if parts.len() >= 2 && !parts[0].is_empty() && !parts[1].is_empty() {
            let base = bitmex_base(parts[0]);
            return Ok(format!("{}{}", base, parts[1].to_ascii_uppercase()));
        }
    }
    if !product_symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '.')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX WebSocket symbol: {product_symbol}"
        )));
    }
    Ok(product_symbol.to_ascii_uppercase())
}

pub(super) fn normalize_table(table: &str) -> Result<String> {
    let table = table.trim();
    if table.is_empty() {
        return Err(DcexError::InvalidInput(
            "BitMEX WebSocket table must not be empty.".to_string(),
        ));
    }
    if !table
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX WebSocket table: {table}"
        )));
    }
    Ok(table.to_string())
}

pub(super) fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

fn bitmex_base(base: &str) -> String {
    if base.eq_ignore_ascii_case("BTC") {
        "XBT".to_string()
    } else {
        base.to_ascii_uppercase()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_symbol_and_subscription_arg() {
        assert_eq!(
            normalize_symbol("BTC-USD-SWAP").expect("canonical"),
            "XBTUSD"
        );
        assert_eq!(normalize_symbol("ethusd").expect("raw"), "ETHUSD");
        assert_eq!(
            subscription_arg("trade", Some("XBTUSD")).expect("symbol table"),
            "trade:XBTUSD"
        );
        assert_eq!(
            subscription_arg("margin", Some("XBTUSD")).expect("no symbol table"),
            "margin"
        );
        assert!(normalize_subscription_arg("trade:XBTUSD").is_ok());
        assert!(normalize_subscription_arg("trade XBTUSD").is_err());
    }
}
