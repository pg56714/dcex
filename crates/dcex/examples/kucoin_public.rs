use std::time::Duration;

use dcex::exchanges::kucoin::KucoinClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = KucoinClient::new(None, None, None, Duration::from_secs(10))?;

    let instruments = client.get_spot_instrument_info(Vec::new()).await?;
    println!("{}", instruments.data);

    let ticker = client
        .get_spot_ticker(vec![(
            "product_symbol".to_string(),
            "BTC-USDT-SPOT".to_string(),
        )])
        .await?;
    println!("{}", ticker.data);

    Ok(())
}
