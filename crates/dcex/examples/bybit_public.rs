use std::time::Duration;

use dcex::exchanges::bybit::BybitClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BybitClient::new(None, None, 5_000, true, Duration::from_secs(10))?;
    let response = client
        .get_orderbook(vec![
            ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
            ("limit".to_string(), "5".to_string()),
        ])
        .await?;
    println!("{}", response.data);
    Ok(())
}
