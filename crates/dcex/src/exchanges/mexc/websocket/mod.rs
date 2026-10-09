mod futures;
#[cfg(test)]
mod futures_tests;
pub use futures::MexcFuturesWebSocket;
mod private;
#[cfg(test)]
mod private_tests;
mod public;
#[cfg(test)]
mod public_tests;

pub use private::MexcPrivateWebSocket;
pub use public::MexcPublicWebSocket;
