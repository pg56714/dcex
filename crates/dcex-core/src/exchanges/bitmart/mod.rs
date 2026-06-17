mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;

pub use client::{BitmartClient, BitmartMarket};

#[cfg(test)]
mod tests;
