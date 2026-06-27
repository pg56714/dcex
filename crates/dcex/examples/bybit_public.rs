use std::time::Duration;

use dcex::exchanges::bybit::BybitClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BybitClient::public(5_000, true, Duration::from_secs(10))?;
    let response = client.get_orderbook("BTC-USDT-SPOT").limit(5).await?;
    println!("{}", response.data);
    Ok(())
}
