use std::time::Duration;

use dcex::exchanges::binance::{BinanceClient, BinanceMarket};
use dcex::http::HttpMethod;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BinanceClient::public(Duration::from_secs(10))?;
    let response = client
        .request_raw(
            HttpMethod::Get,
            BinanceMarket::Spot,
            "/api/v3/time",
            Vec::new(),
            false,
        )
        .await?;
    println!("{}", response.text()?);
    Ok(())
}
