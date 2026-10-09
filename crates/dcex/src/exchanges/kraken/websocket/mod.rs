mod futures;
mod trading;
#[cfg(test)]
mod trading_tests;
pub use futures::KrakenFuturesWebSocket;
mod private;
#[cfg(test)]
mod private_tests;
mod public;
#[cfg(test)]
mod public_tests;

pub use private::KrakenPrivateWebSocket;
pub use public::KrakenPublicWebSocket;

mod v1;
pub use v1::KrakenV1WebSocket;
