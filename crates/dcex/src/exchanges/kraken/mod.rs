mod account;
mod client;
mod earn;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod trading_controls;
mod websocket;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::{KrakenAuth, KrakenClient};
pub use websocket::{KrakenFuturesWebSocket, KrakenPrivateWebSocket, KrakenPublicWebSocket};

mod risk;
mod risk_endpoints;
