use std::time::Duration;

use dcex::exchanges::okx::OkxClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = OkxClient::public(Duration::from_secs(10))?;
    let response = client.get_orderbook("BTC-USDT-SPOT").sz(5).await?;
    println!("{}", response.data);
    Ok(())
}
