use std::time::Duration;

use dcex::exchanges::hyperliquid::HyperliquidClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = HyperliquidClient::public(false, Duration::from_secs(10))?;

    let meta = client.get_meta().await?;
    println!("{}", meta.data);

    let orderbook = client
        .get_l2book_with(vec![(
            "product_symbol".to_string(),
            "BTC-USD-SWAP".to_string(),
        )])
        .await?;
    println!("{}", orderbook.data);

    Ok(())
}
