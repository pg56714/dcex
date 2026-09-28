//! Order side utilities.
use crate::{DcexError, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OrderSide {
    Buy,
    Sell,
}

impl OrderSide {
    pub fn parse(value: &str) -> Result<Self> {
        match value.trim().to_ascii_lowercase().as_str() {
            "buy" => Ok(Self::Buy),
            "sell" => Ok(Self::Sell),
            _ => Err(DcexError::InvalidInput(format!(
                "Unknown order side: {value:?}"
            ))),
        }
    }

    pub const fn is_buy(self) -> bool {
        matches!(self, Self::Buy)
    }

    pub fn to_exchange(self, exchange: &str) -> Result<&'static str> {
        let exchange = exchange.to_ascii_lowercase();
        if matches!(exchange.as_str(), "hyperliquid" | "lighter") {
            return Err(DcexError::InvalidInput(format!(
                "{exchange} expresses side as a boolean; use OrderSide.is_buy() instead"
            )));
        }
        let value = match (self, exchange.as_str()) {
            (Self::Buy, "arcus" | "aster" | "binance" | "bingx" | "mexc") => "BUY",
            (Self::Sell, "arcus" | "aster" | "binance" | "bingx" | "mexc") => "SELL",
            (Self::Buy, "backpack") => "Bid",
            (Self::Sell, "backpack") => "Ask",
            (Self::Buy, "bybit") => "Buy",
            (Self::Sell, "bybit") => "Sell",
            (Self::Buy, "extended") => "BUY",
            (Self::Sell, "extended") => "SELL",
            (Self::Buy, "okx" | "bitget" | "kucoin" | "kraken" | "ondo") => "buy",
            (Self::Sell, "okx" | "bitget" | "kucoin" | "kraken" | "ondo") => "sell",
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "No OrderSide mapping for exchange: {exchange:?}"
                )));
            }
        };
        Ok(value)
    }
}
