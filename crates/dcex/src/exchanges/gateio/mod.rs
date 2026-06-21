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

pub use client::GateioClient;
pub use websocket::{GateioPrivateWebSocket, GateioPublicWebSocket};

#[cfg(test)]
mod tests;
