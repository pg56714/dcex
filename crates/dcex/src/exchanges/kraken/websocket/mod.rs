mod futures;
mod trading;
pub use futures::KrakenFuturesWebSocket;
mod private;
mod public;

pub use private::KrakenPrivateWebSocket;
pub use public::KrakenPublicWebSocket;
