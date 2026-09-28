mod account;
mod classic_trading;
mod client;

mod earn;
mod endpoints;

mod generated;
mod margin;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod uta;
mod websocket;
mod withdrawals;
mod wrappers;

pub use client::{KucoinClient, KucoinMarket};
pub use websocket::{KucoinPrivateWebSocket, KucoinProWebSocket, KucoinPublicWebSocket};

#[cfg(test)]
mod tests;

mod schema_requests;
