use std::time::Duration;

use dcex::exchanges::mexc::MexcClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = MexcClient::new(None, None, Duration::from_secs(10))?;
    let response = client
        .get_spot_orderbook(vec![
            ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
            ("limit".to_string(), "5".to_string()),
        ])
        .await?;
    println!("{}", response.data);
    Ok(())
}
