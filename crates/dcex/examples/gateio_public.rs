use std::time::Duration;

use dcex::exchanges::gateio::GateioClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = GateioClient::public(Duration::from_secs(10))?;
    let response = client.get_spot_order_book("BTC-USDT-SPOT").limit(5).await?;
    println!("{}", response.data);
    Ok(())
}
