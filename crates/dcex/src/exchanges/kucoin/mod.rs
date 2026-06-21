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

pub use client::{KucoinClient, KucoinMarket};
pub use websocket::{KucoinPrivateWebSocket, KucoinPublicWebSocket};

#[cfg(test)]
mod tests;
