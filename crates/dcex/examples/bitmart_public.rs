use std::time::Duration;

use dcex::exchanges::bitmart::BitmartClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BitmartClient::public(Duration::from_secs(10))?;
    let response = client.get_ticker_of_a_pair("BTC-USDT-SPOT").await?;
    println!("{}", response.data);
    Ok(())
}
