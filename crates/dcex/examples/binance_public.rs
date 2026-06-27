use std::time::Duration;

use dcex::exchanges::binance::BinanceClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BinanceClient::public(Duration::from_secs(10))?;
    let response = client.get_spot_orderbook("BTC-USDT-SPOT").await?;
    println!("{}", response.data);
    Ok(())
}
