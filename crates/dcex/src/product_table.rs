use std::collections::HashMap;

use serde::{Deserialize, Serialize};

use crate::{DcexError, Result};

#[path = "product_table_fetch.rs"]
mod fetch;

type UniqueIndex = HashMap<String, HashMap<String, Option<usize>>>;
type MultiIndex = HashMap<String, HashMap<String, Vec<usize>>>;
type TypedUniqueIndex = HashMap<String, HashMap<String, HashMap<String, Option<usize>>>>;

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct MarketInfo {
    pub exchange: String,
    pub exchange_symbol: String,
    pub product_symbol: String,
    pub product_type: String,
    pub exchange_type: String,
    pub price_precision: String,
    pub size_precision: String,
    pub min_size: String,
    pub base_currency: String,
    pub quote_currency: String,
    pub min_notional: String,
    pub size_per_contract: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct TradingDetails {
    pub price_precision: String,
    pub size_precision: String,
    pub min_size: String,
    pub min_notional: String,
    pub size_per_contract: String,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct ProductFilter<'a> {
    pub product_symbol: Option<&'a str>,
    pub exchange: Option<&'a str>,
    pub product_type: Option<&'a str>,
    pub exchange_type: Option<&'a str>,
    pub exchange_symbol: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct ProductTable {
    rows: Vec<MarketInfo>,
    by_exchange_product: UniqueIndex,
    by_exchange_exchange_symbol: MultiIndex,
    by_exchange_exchange_symbol_product_type: TypedUniqueIndex,
    by_exchange_exchange_symbol_exchange_type: TypedUniqueIndex,
}

impl ProductTable {
    pub fn new(rows: Vec<MarketInfo>) -> Self {
        let mut table = Self {
            rows,
            ..Self::default()
        };
        table.build_indexes();
        table
    }

    pub fn rows(&self) -> &[MarketInfo] {
        &self.rows
    }

    pub fn into_rows(self) -> Vec<MarketInfo> {
        self.rows
    }

    pub async fn fetch(
        exchange: Option<crate::exchange::Exchange>,
        timeout: std::time::Duration,
    ) -> Result<Self> {
        fetch::fetch_product_rows(exchange, timeout)
            .await
            .map(Self::new)
    }

    pub fn get(&self, key: &str, filter: ProductFilter<'_>) -> Result<String> {
        let matches = self
            .rows
            .iter()
            .filter(|row| row_matches(row, filter))
            .collect::<Vec<_>>();

        if matches.len() > 1 {
            return Err(product_table_error(format!(
                "Exist multiple {key} for product_symbol: {}, exchange: {}, product_type: {}",
                display_option(filter.product_symbol),
                display_option(filter.exchange),
                display_option(filter.product_type)
            )));
        }
        let row = matches.first().ok_or_else(|| {
            product_table_error(format!(
                "Not exist {key} for product_symbol: {}, exchange: {}, product_type: {}, exchange_symbol: {}",
                display_option(filter.product_symbol),
                display_option(filter.exchange),
                display_option(filter.product_type),
                display_option(filter.exchange_symbol)
            ))
        })?;
        row_value(row, key)
            .map(str::to_string)
            .ok_or_else(|| product_table_error(format!("Key not found: {key}")))
    }

    pub fn get_exchange_symbol(&self, exchange: &str, product_symbol: &str) -> Result<String> {
        match lookup_unique_index(&self.by_exchange_product, exchange, product_symbol) {
            Some(Some(index)) => Ok(self.rows[index].exchange_symbol.clone()),
            _ => self.get(
                "exchange_symbol",
                ProductFilter {
                    exchange: Some(exchange),
                    product_symbol: Some(product_symbol),
                    ..ProductFilter::default()
                },
            ),
        }
    }

    pub fn get_product_symbol(
        &self,
        exchange: &str,
        exchange_symbol: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Result<String> {
        if product_type.is_none() && exchange_type.is_none() {
            return Err(product_table_error(
                "You must specify either product_type or exchange_type".to_string(),
            ));
        }

        if let Some(index) =
            self.indexed_product_symbol(exchange, exchange_symbol, product_type, exchange_type)
        {
            return Ok(self.rows[index].product_symbol.clone());
        }

        self.get(
            "product_symbol",
            ProductFilter {
                exchange: Some(exchange),
                exchange_symbol: Some(exchange_symbol),
                product_type,
                exchange_type,
                ..ProductFilter::default()
            },
        )
    }

    pub fn get_product_type(
        &self,
        exchange: &str,
        product_symbol: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> Result<String> {
        self.get_product_field("product_type", exchange, product_symbol, exchange_symbol)
    }

    pub fn get_exchange_type(
        &self,
        exchange: &str,
        product_symbol: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> Result<String> {
        self.get_product_field("exchange_type", exchange, product_symbol, exchange_symbol)
    }

    pub fn get_base_currency(&self, exchange: &str, product_symbol: &str) -> Result<String> {
        self.get_product_value("base_currency", exchange, product_symbol)
    }

    pub fn get_quote_currency(&self, exchange: &str, product_symbol: &str) -> Result<String> {
        self.get_product_value("quote_currency", exchange, product_symbol)
    }

    pub fn get_trading_details(
        &self,
        exchange: &str,
        product_symbol: &str,
    ) -> Result<TradingDetails> {
        let row = self.unique_product(exchange, product_symbol)?;
        Ok(TradingDetails {
            price_precision: row.price_precision.clone(),
            size_precision: row.size_precision.clone(),
            min_size: row.min_size.clone(),
            min_notional: row.min_notional.clone(),
            size_per_contract: row.size_per_contract.clone(),
        })
    }

    pub fn get_exchange_symbols(
        &self,
        exchange: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Vec<String> {
        self.filtered_symbols(exchange, product_type, exchange_type, |row| {
            row.exchange_symbol.clone()
        })
    }

    pub fn get_product_symbols(
        &self,
        exchange: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Vec<String> {
        self.filtered_symbols(exchange, product_type, exchange_type, |row| {
            row.product_symbol.clone()
        })
    }

    fn build_indexes(&mut self) {
        for (index, row) in self.rows.iter().enumerate() {
            insert_unique_index(
                &mut self.by_exchange_product,
                &row.exchange,
                &row.product_symbol,
                index,
            );
            insert_multi_index(
                &mut self.by_exchange_exchange_symbol,
                &row.exchange,
                &row.exchange_symbol,
                index,
            );
            insert_typed_unique_index(
                &mut self.by_exchange_exchange_symbol_product_type,
                &row.exchange,
                &row.exchange_symbol,
                &row.product_type,
                index,
            );
            insert_typed_unique_index(
                &mut self.by_exchange_exchange_symbol_exchange_type,
                &row.exchange,
                &row.exchange_symbol,
                &row.exchange_type,
                index,
            );
        }
    }

    fn indexed_product_symbol(
        &self,
        exchange: &str,
        exchange_symbol: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Option<usize> {
        let index = match (product_type, exchange_type) {
            (Some(product_type), None) => lookup_typed_unique_index(
                &self.by_exchange_exchange_symbol_product_type,
                exchange,
                exchange_symbol,
                product_type,
            )
            .flatten(),
            (None, Some(exchange_type)) => lookup_typed_unique_index(
                &self.by_exchange_exchange_symbol_exchange_type,
                exchange,
                exchange_symbol,
                exchange_type,
            )
            .flatten(),
            (Some(product_type), Some(exchange_type)) => lookup_typed_unique_index(
                &self.by_exchange_exchange_symbol_product_type,
                exchange,
                exchange_symbol,
                product_type,
            )
            .flatten()
            .filter(|index| self.rows[*index].exchange_type == exchange_type),
            (None, None) => None,
        };
        index
    }

    fn get_product_field(
        &self,
        key: &str,
        exchange: &str,
        product_symbol: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> Result<String> {
        if let Some(product_symbol) = product_symbol {
            return self.get_product_value(key, exchange, product_symbol);
        }
        if let Some(exchange_symbol) = exchange_symbol {
            if let Some(indexes) =
                lookup_multi_index(&self.by_exchange_exchange_symbol, exchange, exchange_symbol)
            {
                if indexes.len() == 1 {
                    return row_value(&self.rows[indexes[0]], key)
                        .map(str::to_string)
                        .ok_or_else(|| product_table_error(format!("Key not found: {key}")));
                }
            }
            return self.get(
                key,
                ProductFilter {
                    exchange: Some(exchange),
                    exchange_symbol: Some(exchange_symbol),
                    ..ProductFilter::default()
                },
            );
        }
        Err(product_table_error(
            "You must specify either product_symbol or exchange_symbol".to_string(),
        ))
    }

    fn get_product_value(&self, key: &str, exchange: &str, product_symbol: &str) -> Result<String> {
        let row = self.unique_product(exchange, product_symbol)?;
        row_value(row, key)
            .map(str::to_string)
            .ok_or_else(|| product_table_error(format!("Key not found: {key}")))
    }

    fn unique_product(&self, exchange: &str, product_symbol: &str) -> Result<&MarketInfo> {
        match lookup_unique_index(&self.by_exchange_product, exchange, product_symbol) {
            Some(Some(index)) => Ok(&self.rows[index]),
            _ => {
                let matches = self
                    .rows
                    .iter()
                    .filter(|row| row.exchange == exchange && row.product_symbol == product_symbol)
                    .collect::<Vec<_>>();
                if matches.len() == 1 {
                    Ok(matches[0])
                } else if matches.is_empty() {
                    Err(product_table_error(format!(
                        "Not exist product for product_symbol: {product_symbol}, exchange: {exchange}"
                    )))
                } else {
                    Err(product_table_error(format!(
                        "Exist multiple product for product_symbol: {product_symbol}, exchange: {exchange}"
                    )))
                }
            }
        }
    }

    fn filtered_symbols(
        &self,
        exchange: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
        value: impl Fn(&MarketInfo) -> String,
    ) -> Vec<String> {
        self.rows
            .iter()
            .filter(|row| {
                row.exchange == exchange
                    && product_type.is_none_or(|kind| row.product_type == kind)
                    && exchange_type.is_none_or(|kind| row.exchange_type == kind)
            })
            .map(value)
            .collect()
    }
}

fn insert_unique_index(
    index: &mut UniqueIndex,
    exchange: &str,
    symbol: &str,
    row_index: usize,
) {
    index
        .entry(exchange.to_string())
        .or_default()
        .entry(symbol.to_string())
        .and_modify(|value| *value = None)
        .or_insert(Some(row_index));
}

fn lookup_unique_index(index: &UniqueIndex, exchange: &str, symbol: &str) -> Option<Option<usize>> {
    index.get(exchange)?.get(symbol).copied()
}

fn insert_multi_index(index: &mut MultiIndex, exchange: &str, symbol: &str, row_index: usize) {
    index
        .entry(exchange.to_string())
        .or_default()
        .entry(symbol.to_string())
        .or_default()
        .push(row_index);
}

fn lookup_multi_index<'a>(
    index: &'a MultiIndex,
    exchange: &str,
    symbol: &str,
) -> Option<&'a [usize]> {
    index.get(exchange)?.get(symbol).map(Vec::as_slice)
}

fn insert_typed_unique_index(
    index: &mut TypedUniqueIndex,
    exchange: &str,
    symbol: &str,
    kind: &str,
    row_index: usize,
) {
    index
        .entry(exchange.to_string())
        .or_default()
        .entry(symbol.to_string())
        .or_default()
        .entry(kind.to_string())
        .and_modify(|value| *value = None)
        .or_insert(Some(row_index));
}

fn lookup_typed_unique_index(
    index: &TypedUniqueIndex,
    exchange: &str,
    symbol: &str,
    kind: &str,
) -> Option<Option<usize>> {
    index.get(exchange)?.get(symbol)?.get(kind).copied()
}

fn row_matches(row: &MarketInfo, filter: ProductFilter<'_>) -> bool {
    filter
        .product_symbol
        .is_none_or(|value| row.product_symbol == value)
        && filter.exchange.is_none_or(|value| row.exchange == value)
        && filter
            .product_type
            .is_none_or(|value| row.product_type == value)
        && filter
            .exchange_type
            .is_none_or(|value| row.exchange_type == value)
        && filter
            .exchange_symbol
            .is_none_or(|value| row.exchange_symbol == value)
}

fn row_value<'a>(row: &'a MarketInfo, key: &str) -> Option<&'a str> {
    match key {
        "exchange" => Some(&row.exchange),
        "exchange_symbol" => Some(&row.exchange_symbol),
        "product_symbol" => Some(&row.product_symbol),
        "product_type" => Some(&row.product_type),
        "exchange_type" => Some(&row.exchange_type),
        "price_precision" => Some(&row.price_precision),
        "size_precision" => Some(&row.size_precision),
        "min_size" => Some(&row.min_size),
        "base_currency" => Some(&row.base_currency),
        "quote_currency" => Some(&row.quote_currency),
        "min_notional" => Some(&row.min_notional),
        "size_per_contract" => Some(&row.size_per_contract),
        _ => None,
    }
}

fn display_option(value: Option<&str>) -> &str {
    value.unwrap_or("None")
}

fn product_table_error(message: String) -> DcexError {
    DcexError::InvalidInput(message)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn row(
        exchange: &str,
        product_symbol: &str,
        exchange_symbol: &str,
        product_type: &str,
        exchange_type: &str,
    ) -> MarketInfo {
        MarketInfo {
            exchange: exchange.to_string(),
            product_symbol: product_symbol.to_string(),
            exchange_symbol: exchange_symbol.to_string(),
            product_type: product_type.to_string(),
            exchange_type: exchange_type.to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USDT".to_string(),
            price_precision: "0.1".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0.001".to_string(),
            min_notional: "5".to_string(),
            size_per_contract: "1".to_string(),
        }
    }

    fn table() -> ProductTable {
        ProductTable::new(vec![
            row("binance", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
            row("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
            row("okx", "ETH-USDT-SWAP", "ETH-USDT-SWAP", "swap", "SWAP"),
        ])
    }

    #[test]
    fn resolves_symbols_in_both_directions() {
        let table = table();
        assert_eq!(
            table
                .get_exchange_symbol("binance", "BTC-USDT-SPOT")
                .expect("exchange symbol"),
            "BTCUSDT"
        );
        assert_eq!(
            table
                .get_product_symbol("binance", "BTCUSDT", Some("swap"), None)
                .expect("product symbol"),
            "BTC-USDT-SWAP"
        );
        assert_eq!(
            table
                .get_product_symbol("binance", "BTCUSDT", None, Some("PERPETUAL"))
                .expect("product symbol"),
            "BTC-USDT-SWAP"
        );
    }

    #[test]
    fn rejects_ambiguous_exchange_symbol() {
        let table = ProductTable::new(vec![
            row(
                "example",
                "BTC-USD-2026-FUTURES",
                "BTCUSD",
                "futures",
                "dated-2026",
            ),
            row(
                "example",
                "BTC-USD-2027-FUTURES",
                "BTCUSD",
                "futures",
                "dated-2027",
            ),
        ]);

        assert!(table
            .get_product_symbol("example", "BTCUSD", Some("futures"), None)
            .is_err());
        assert_eq!(
            table
                .get_product_symbol("example", "BTCUSD", Some("futures"), Some("dated-2026"),)
                .expect("dated product"),
            "BTC-USD-2026-FUTURES"
        );
    }

    #[test]
    fn returns_trading_details_and_symbol_lists() {
        let table = table();
        assert_eq!(
            table
                .get_trading_details("binance", "BTC-USDT-SWAP")
                .expect("trading details")
                .min_notional,
            "5"
        );
        assert_eq!(
            table.get_product_symbols("binance", Some("spot"), None),
            vec!["BTC-USDT-SPOT"]
        );
    }
}
