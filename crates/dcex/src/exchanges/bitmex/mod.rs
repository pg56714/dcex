mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod position;
mod private;
mod signing;
mod trade;
mod trading;
pub mod websocket;
mod wrappers;

pub use client::BitmexClient;
pub use websocket::{BitmexPrivateWebSocket, BitmexPublicWebSocket};

#[cfg(test)]
mod tests;
