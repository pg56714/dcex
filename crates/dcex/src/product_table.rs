use std::collections::HashMap;

use serde::{Deserialize, Serialize};

use crate::{DcexError, Result};

#[path = "product_table_fetch.rs"]
mod fetch;

#[cfg(test)]
pub(crate) use fetch::kraken_spot_rows;

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
    /// Another official native name for the same market (Kraken AssetPairs `altname`
    /// or pair key); empty when the exchange publishes only one.
    #[serde(default)]
    pub exchange_symbol_alias: String,
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
    /// Every row of a canonical product symbol, per exchange namespace.
    by_exchange_product_rows: MultiIndex,
    /// Other exact names a row answers to: its alias, and `BASE/QUOTE` for Kraken spot.
    by_exchange_alternate_symbol: MultiIndex,
    /// Hyperliquid rows by coin name, with the asset id of their `["COIN", id]` symbol.
    hyperliquid_coins: HashMap<String, Vec<(usize, u64)>>,
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

    pub async fn fetch(
        exchange: Option<crate::exchange::Exchange>,
        timeout: std::time::Duration,
    ) -> Result<Self> {
        fetch::fetch_product_rows(exchange, timeout)
            .await
            .map(Self::new)
    }

    /// Hyperliquid's table limited to the named builder-deployed (HIP-3) perp DEXs; the
    /// first perp DEX and spot always load. Unknown names are rejected.
    pub async fn fetch_hyperliquid(
        perp_dexs: Option<&[String]>,
        timeout: std::time::Duration,
    ) -> Result<Self> {
        fetch::fetch_hyperliquid_rows(perp_dexs, timeout)
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

    /// Resolve an exact canonical or native symbol within the method's market scope.
    /// Canonical matches take precedence; unknown and ambiguous names never fall back.
    pub fn resolve_symbol(
        &self,
        exchange: &str,
        symbol: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Result<&MarketInfo> {
        self.resolve_symbol_in(exchange, symbol, |row| {
            product_type.is_none_or(|kind| row.product_type == kind)
                && exchange_type.is_none_or(|kind| row.exchange_type == kind)
        })
    }

    /// Apply the endpoint's explicit market constraints to exact symbol matches.
    pub fn resolve_symbol_in(
        &self,
        exchange: &str,
        symbol: &str,
        accepts: impl Fn(&MarketInfo) -> bool,
    ) -> Result<&MarketInfo> {
        self.resolve_symbol_across(&[exchange], symbol, accepts)
    }

    /// Resolve across several table namespaces of one venue (e.g. `binance` and `binance_coinm`).
    pub fn resolve_symbol_across(
        &self,
        exchanges: &[&str],
        symbol: &str,
        accepts: impl Fn(&MarketInfo) -> bool,
    ) -> Result<&MarketInfo> {
        let canonical = self.has_product_symbol(exchanges, symbol);
        // Every name a row answers to is indexed, so no call scans the table.
        let mut positions: Vec<usize> = Vec::new();
        for exchange in exchanges {
            if canonical {
                positions.extend(
                    lookup_multi_index(&self.by_exchange_product_rows, exchange, symbol)
                        .unwrap_or_default(),
                );
                continue;
            }
            for index in [
                &self.by_exchange_exchange_symbol,
                &self.by_exchange_alternate_symbol,
            ] {
                positions.extend(lookup_multi_index(index, exchange, symbol).unwrap_or_default());
            }
            if *exchange == "hyperliquid" {
                positions.extend(self.hyperliquid_positions(symbol));
            }
        }
        // Table order, each row once: a row can be reached through more than one name.
        positions.sort_unstable();
        positions.dedup();
        let candidates: Vec<_> = positions
            .iter()
            .map(|position| &self.rows[*position])
            .collect();
        let matches: Vec<_> = candidates
            .iter()
            .copied()
            .filter(|row| accepts(row))
            .collect();
        match matches.as_slice() {
            [row] => Ok(row),
            _ => {
                let names = candidates
                    .iter()
                    .map(|row| row.product_symbol.as_str())
                    .collect::<Vec<_>>()
                    .join(", ");
                let exchange = exchanges.join("/");
                Err(product_table_error(format!(
                    "Cannot resolve {exchange} symbol {symbol:?} within the requested market; candidates: [{names}]"
                )))
            }
        }
    }

    /// Hyperliquid rows named by `symbol`: the coin alone, or the exact `["COIN", id]` pair.
    fn hyperliquid_positions(&self, symbol: &str) -> Vec<usize> {
        let (coin, id) = match serde_json::from_str::<(String, u64)>(symbol) {
            Ok((coin, id)) => (coin, Some(id)),
            Err(_) => (symbol.to_string(), None),
        };
        self.hyperliquid_coins
            .get(&coin)
            .into_iter()
            .flatten()
            .filter(|(_, row_id)| id.is_none_or(|id| id == *row_id))
            .map(|(position, _)| *position)
            .collect()
    }

    /// Whether `symbol` is a canonical product symbol in any of the namespaces.
    pub(crate) fn has_product_symbol(&self, exchanges: &[&str], symbol: &str) -> bool {
        exchanges.iter().any(|exchange| {
            lookup_unique_index(&self.by_exchange_product, exchange, symbol).is_some()
        })
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
            insert_multi_index(
                &mut self.by_exchange_product_rows,
                &row.exchange,
                &row.product_symbol,
                index,
            );
            if !row.exchange_symbol_alias.is_empty() {
                insert_multi_index(
                    &mut self.by_exchange_alternate_symbol,
                    &row.exchange,
                    &row.exchange_symbol_alias,
                    index,
                );
            }
            if row.exchange == "kraken"
                && row.product_type == "spot"
                && !row.base_currency.is_empty()
                && !row.quote_currency.is_empty()
            {
                insert_multi_index(
                    &mut self.by_exchange_alternate_symbol,
                    &row.exchange,
                    &format!("{}/{}", row.base_currency, row.quote_currency),
                    index,
                );
            }
            if row.exchange == "hyperliquid"
                && let Ok((coin, id)) = serde_json::from_str::<(String, u64)>(&row.exchange_symbol)
            {
                self.hyperliquid_coins
                    .entry(coin)
                    .or_default()
                    .push((index, id));
            }
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
        match (product_type, exchange_type) {
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
        }
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
                && indexes.len() == 1
            {
                return row_value(&self.rows[indexes[0]], key)
                    .map(str::to_string)
                    .ok_or_else(|| product_table_error(format!("Key not found: {key}")));
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

fn insert_unique_index(index: &mut UniqueIndex, exchange: &str, symbol: &str, row_index: usize) {
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
        "exchange_symbol_alias" => Some(&row.exchange_symbol_alias),
        _ => None,
    }
}

/// Hyperliquid rows store `[coin, asset_id]` JSON; compare parsed pairs, or the coin alone.
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
            ..MarketInfo::default()
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
    fn exact_resolver_requires_a_unique_market_and_preserves_case() {
        let table = table();
        assert_eq!(
            table
                .resolve_symbol("binance", "BTC-USDT-SPOT", Some("spot"), None)
                .unwrap()
                .exchange_symbol,
            "BTCUSDT"
        );
        assert_eq!(
            table
                .resolve_symbol("binance", "BTCUSDT", Some("swap"), None)
                .unwrap()
                .product_symbol,
            "BTC-USDT-SWAP"
        );
        let error = table
            .resolve_symbol("binance", "BTCUSDT", None, None)
            .unwrap_err()
            .to_string();
        assert!(error.contains("BTC-USDT-SPOT") && error.contains("BTC-USDT-SWAP"));
        assert!(
            table
                .resolve_symbol("binance", "btcusdt", None, None)
                .is_err()
        );
        assert!(
            table
                .resolve_symbol("binance", "BTC-USDT-SPOT", Some("swap"), None)
                .is_err()
        );
        assert!(table.resolve_symbol("binance", "BTC", None, None).is_err());
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

        assert!(
            table
                .get_product_symbol("example", "BTCUSD", Some("futures"), None)
                .is_err()
        );
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

    #[test]
    fn resolution_only_sees_the_requested_namespaces() {
        let mut kraken = row("kraken", "BTC-USD-SPOT", "XXBTZUSD", "spot", "spot");
        kraken.quote_currency = "USD".to_string();
        let table = ProductTable::new(vec![
            row("okx", "BTC-USDT-SWAP", "BTC-USDT-SWAP", "swap", "SWAP"),
            row("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
            kraken,
            row(
                "binance_coinm",
                "BTC-USD-SWAP",
                "BTCUSD_PERP",
                "swap",
                "PERPETUAL",
            ),
            row("binance", "ETH-USDT-SWAP", "ETHUSDT", "swap", "PERPETUAL"),
        ]);

        assert!(table.has_product_symbol(&["binance"], "BTC-USDT-SWAP"));
        assert!(!table.has_product_symbol(&["binance"], "BTC-USD-SWAP"));
        assert!(table.has_product_symbol(&["binance", "binance_coinm"], "BTC-USD-SWAP"));
        assert!(!table.has_product_symbol(&["binance"], "BTCUSDT"));

        // The same canonical name on another exchange is not a candidate.
        let swap = table
            .resolve_symbol("binance", "BTC-USDT-SWAP", None, None)
            .expect("binance swap");
        assert_eq!(swap.exchange_symbol, "BTCUSDT");
        for (symbol, native) in [("BTCUSD_PERP", "BTCUSD_PERP"), ("ETHUSDT", "ETHUSDT")] {
            let row = table
                .resolve_symbol_across(&["binance", "binance_coinm"], symbol, |_| true)
                .expect("across namespaces");
            assert_eq!(row.exchange_symbol, native);
        }
        assert!(table.resolve_symbol("okx", "BTCUSDT", None, None).is_err());
        assert!(
            table
                .resolve_symbol("bybit", "BTC-USDT-SWAP", None, None)
                .is_err()
        );

        // Kraken spot also answers to BASE/QUOTE, and only to that exact pair.
        let spot = table
            .resolve_symbol("kraken", "BTC/USD", None, None)
            .expect("kraken pair");
        assert_eq!(spot.exchange_symbol, "XXBTZUSD");
        for symbol in ["BTC/USDT", "BTC/US", "BTCUSD", "BTC//USD", "/USD", "BTC/"] {
            assert!(
                table.resolve_symbol("kraken", symbol, None, None).is_err(),
                "{symbol}"
            );
        }
    }

    /// The resolver's contract, written as the plain scan the indexes replace.
    fn scanned<'a>(
        table: &'a ProductTable,
        exchanges: &[&str],
        symbol: &str,
    ) -> Vec<&'a MarketInfo> {
        let named = |row: &MarketInfo| exchanges.contains(&row.exchange.as_str());
        let canonical = table
            .rows()
            .iter()
            .any(|row| named(row) && row.product_symbol == symbol);
        let hyperliquid = |row: &MarketInfo| {
            let Ok(native) = serde_json::from_str::<(String, u64)>(&row.exchange_symbol) else {
                return false;
            };
            match serde_json::from_str::<(String, u64)>(symbol) {
                Ok(input) => input == native,
                Err(_) => native.0 == symbol,
            }
        };
        table
            .rows()
            .iter()
            .filter(|row| {
                named(row)
                    && if canonical {
                        row.product_symbol == symbol
                    } else {
                        row.exchange_symbol == symbol
                            || (!row.exchange_symbol_alias.is_empty()
                                && row.exchange_symbol_alias == symbol)
                            || (row.exchange == "kraken"
                                && row.product_type == "spot"
                                && !row.base_currency.is_empty()
                                && !row.quote_currency.is_empty()
                                && format!("{}/{}", row.base_currency, row.quote_currency)
                                    == symbol)
                            || (row.exchange == "hyperliquid" && hyperliquid(row))
                    }
            })
            .collect()
    }

    #[test]
    fn indexed_resolution_matches_a_full_scan() {
        let with = |mut row: MarketInfo, alias: &str, base: &str, quote: &str| {
            row.exchange_symbol_alias = alias.to_string();
            row.base_currency = base.to_string();
            row.quote_currency = quote.to_string();
            row
        };
        let table = ProductTable::new(vec![
            row("binance", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
            row("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
            row(
                "binance_coinm",
                "BTC-USD-SWAP",
                "BTCUSD_PERP",
                "swap",
                "PERPETUAL",
            ),
            // The same canonical symbol twice, and an alias that is another row's native name.
            row("binance", "ETH-USDT-SWAP", "ETHUSDT", "swap", "PERPETUAL"),
            with(
                row("binance", "ETH-USDT-SWAP", "ETHUSDT_2", "swap", "PERPETUAL"),
                "ETHUSDT",
                "ETH",
                "USDT",
            ),
            row("okx", "BTC-USDT-SWAP", "BTC-USDT-SWAP", "swap", "SWAP"),
            with(
                row("kraken", "BTC-USD-SPOT", "XXBTZUSD", "spot", "spot"),
                "XBTUSD",
                "BTC",
                "USD",
            ),
            // A pair name that is also this row's alias: one row, reached twice.
            with(
                row("kraken", "ETH-USD-SPOT", "XETHZUSD", "spot", "spot"),
                "ETH/USD",
                "ETH",
                "USD",
            ),
            with(
                row("kraken", "BTC-USD-SWAP", "PF_XBTUSD", "swap", "futures"),
                "",
                "BTC",
                "USD",
            ),
            with(
                row("kraken", "SOL-USD-SPOT", "SOLUSD", "spot", "spot"),
                "",
                "",
                "USD",
            ),
            row(
                "hyperliquid",
                "BTC-USDC-SWAP",
                r#"["BTC",0]"#,
                "swap",
                "perp",
            ),
            row(
                "hyperliquid",
                "BTC-USDC-SPOT",
                r#"["BTC",10142]"#,
                "spot",
                "spot",
            ),
            row(
                "hyperliquid",
                "ETH-USDC-SWAP",
                r#"["ETH",1]"#,
                "swap",
                "perp",
            ),
            row("hyperliquid", "RAW-USDC-SWAP", "RAW", "swap", "perp"),
            // Not Hyperliquid: the pair form must not be read as one here.
            row("okx", "ODD-USDT-SWAP", r#"["BTC",0]"#, "swap", "SWAP"),
        ]);
        let namespaces: [&[&str]; 9] = [
            &["binance"],
            &["binance_coinm"],
            &["binance", "binance_coinm"],
            &["binance", "binance"],
            &["okx"],
            &["kraken"],
            &["hyperliquid"],
            &["hyperliquid", "okx"],
            &["bybit"],
        ];
        let mut symbols: Vec<String> = table
            .rows()
            .iter()
            .flat_map(|row| {
                [
                    row.product_symbol.clone(),
                    row.exchange_symbol.clone(),
                    row.exchange_symbol_alias.clone(),
                    format!("{}/{}", row.base_currency, row.quote_currency),
                ]
            })
            .collect();
        symbols.extend(
            [
                "",
                "BTC",
                "ETH",
                "RAW",
                "/USD",
                "BTC/",
                "BTC//USD",
                "btcusdt",
                "NOPE",
                r#"["BTC", 0]"#,
                r#"["BTC",1]"#,
                r#"["ETH",1]"#,
                r#"["BTC"]"#,
                r#"["RAW",0]"#,
            ]
            .map(str::to_string),
        );
        let mut resolved = 0;
        for exchanges in namespaces {
            for symbol in &symbols {
                let expected = scanned(&table, exchanges, symbol);
                match table.resolve_symbol_across(exchanges, symbol, |_| true) {
                    Ok(row) => {
                        resolved += 1;
                        assert_eq!(expected, vec![row], "{exchanges:?} {symbol:?}");
                    }
                    Err(error) => {
                        assert_ne!(expected.len(), 1, "{exchanges:?} {symbol:?}: {error}");
                        // The error lists every candidate, in table order.
                        let names = expected
                            .iter()
                            .map(|row| row.product_symbol.as_str())
                            .collect::<Vec<_>>()
                            .join(", ");
                        assert!(
                            error
                                .to_string()
                                .contains(&format!("candidates: [{names}]")),
                            "{exchanges:?} {symbol:?}: {error}"
                        );
                    }
                }
            }
        }
        assert!(resolved > 40, "only {resolved} lookups resolved");
    }
}
