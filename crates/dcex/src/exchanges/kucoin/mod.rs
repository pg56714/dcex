mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod wrappers;

pub use client::{KucoinClient, KucoinMarket};

#[cfg(test)]
mod tests;
