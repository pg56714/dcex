use std::time::Duration;

use dcex::exchanges::bingx::BingxClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BingxClient::new(None, None, Duration::from_secs(10))?;
    let response = client
        .get_orderbook(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("limit".to_string(), "5".to_string()),
        ])
        .await?;
    println!("{}", response.data);
    Ok(())
}
