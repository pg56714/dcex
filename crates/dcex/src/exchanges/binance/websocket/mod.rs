mod api;
mod api_methods;
#[cfg(test)]
mod api_methods_tests;
mod api_schema;
mod api_validation;
pub use api::{BinanceWebSocketApi, BinanceWebSocketApiMarket};
mod equity;
mod private;
mod public;

pub use equity::BinanceEquityWebSocket;
pub use private::BinancePrivateWebSocket;
pub use public::BinancePublicWebSocket;
