mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod wrappers;

pub use client::GateioClient;

#[cfg(test)]
mod tests;
