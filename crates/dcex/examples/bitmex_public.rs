use std::time::Duration;

use dcex::exchanges::bitmex::BitmexClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BitmexClient::public(Duration::from_secs(10))?;
    let response = client.get_orderbook("XBT-USDT-SWAP").await?;
    println!("{}", response.data);
    Ok(())
}
