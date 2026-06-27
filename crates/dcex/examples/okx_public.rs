use std::time::Duration;

use dcex::exchanges::okx::OkxClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = OkxClient::public(Duration::from_secs(10))?;
    let response = client
        .get_orderbook_with(vec![
            ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
            ("sz".to_string(), "5".to_string()),
        ])
        .await?;
    println!("{}", response.data);
    Ok(())
}
