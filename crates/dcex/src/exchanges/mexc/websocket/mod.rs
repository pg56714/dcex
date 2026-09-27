mod futures;
pub use futures::MexcFuturesWebSocket;
mod private;
mod public;

pub use private::MexcPrivateWebSocket;
pub use public::MexcPublicWebSocket;
