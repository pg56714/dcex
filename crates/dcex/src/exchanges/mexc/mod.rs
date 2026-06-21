mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod websocket;
mod wrappers;

pub use client::{MexcApi, MexcClient};
pub use websocket::{MexcPrivateWebSocket, MexcPublicWebSocket};

#[cfg(test)]
mod tests;
