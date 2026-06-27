use std::time::Duration;

use dcex::exchanges::mexc::MexcClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = MexcClient::public(Duration::from_secs(10))?;
    let response = client.get_spot_orderbook("BTC-USDT-SPOT").limit(5).await?;
    println!("{}", response.data);
    Ok(())
}
