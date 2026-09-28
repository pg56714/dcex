//! Arcus perpetuals REST API and the separate Spot RFQ router.

mod client;
mod completion;
mod completion_wrappers;
mod endpoints;
mod market;
mod metadata;
mod onboarding;
mod params;
mod signing;
mod trade;
mod wallet;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::{ArcusClient, ArcusSpotClient};

mod query_validation;
