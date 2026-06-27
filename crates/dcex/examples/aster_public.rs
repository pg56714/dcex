use std::time::Duration;

use dcex::exchanges::aster::AsterClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = AsterClient::public(Duration::from_secs(10))?;
    let response = client.get_futures_orderbook("BTC-USDT-SWAP").await?;
    println!("{}", response.data);
    Ok(())
}
