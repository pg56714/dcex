mod api;
mod api_methods;
#[cfg(test)]
mod api_methods_tests;
mod api_schema;
mod api_validation;
#[cfg(test)]
mod api_validation_tests;
pub use api::{BinanceWebSocketApi, BinanceWebSocketApiMarket};
mod equity;
#[cfg(test)]
mod equity_tests;
mod private;
mod public;

pub use equity::BinanceEquityWebSocket;
pub use private::BinancePrivateWebSocket;
pub use public::BinancePublicWebSocket;
