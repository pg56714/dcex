use std::time::Duration;

use dcex::exchanges::kucoin::KucoinClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = KucoinClient::public(Duration::from_secs(10))?;

    let instruments = client.get_spot_instrument_info().await?;
    println!("{}", instruments.data);

    let ticker = client.get_spot_ticker("BTC-USDT-SPOT").await?;
    println!("{}", ticker.data);

    Ok(())
}
