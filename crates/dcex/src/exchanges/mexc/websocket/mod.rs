mod futures;
pub use futures::MexcFuturesWebSocket;
mod private;
#[cfg(test)]
mod private_tests;
mod public;

pub use private::MexcPrivateWebSocket;
pub use public::MexcPublicWebSocket;
