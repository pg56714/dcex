mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
pub mod websocket;
mod wrappers;

pub use client::{BitmartClient, BitmartMarket};
pub use websocket::{BitmartPrivateWebSocket, BitmartPublicWebSocket};

#[cfg(test)]
mod tests;
