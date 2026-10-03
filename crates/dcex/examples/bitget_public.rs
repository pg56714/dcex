use std::time::Duration;

use dcex::exchanges::bitget::BitgetClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BitgetClient::public(Duration::from_secs(10))?;
    let response = client
        .get_uta_orderbook("SPOT", "BTC-USDT-SPOT")
        .limit(5)
        .await?;
    println!("{}", response.data);
    Ok(())
}
