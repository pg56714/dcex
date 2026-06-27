use std::time::Duration;

use dcex::exchanges::bingx::BingxClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BingxClient::public(Duration::from_secs(10))?;
    let response = client.get_orderbook("BTC-USDT-SWAP").limit(5).await?;
    println!("{}", response.data);
    Ok(())
}
