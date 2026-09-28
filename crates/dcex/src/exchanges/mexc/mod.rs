mod account;
mod client;
mod completion;
mod completion_wrappers;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod websocket;
mod wrappers;

pub use client::{MexcApi, MexcClient};
pub use websocket::{MexcFuturesWebSocket, MexcPrivateWebSocket, MexcPublicWebSocket};

#[cfg(test)]
mod tests;

mod additional;
