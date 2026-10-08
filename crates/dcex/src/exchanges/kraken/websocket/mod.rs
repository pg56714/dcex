mod futures;
mod trading;
pub use futures::KrakenFuturesWebSocket;
mod private;
#[cfg(test)]
mod private_tests;
mod public;

pub use private::KrakenPrivateWebSocket;
pub use public::KrakenPublicWebSocket;

mod v1;
pub use v1::KrakenV1WebSocket;
