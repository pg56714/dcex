use std::time::Duration;

use dcex::exchanges::kraken::KrakenClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = KrakenClient::new(None, None, None, None, Duration::from_secs(10))?;
    let response = client
        .get_spot_ticker(vec![(
            "product_symbol".to_string(),
            "BTC-USDT-SPOT".to_string(),
        )])
        .await?;
    println!("{}", response.data);
    Ok(())
}
