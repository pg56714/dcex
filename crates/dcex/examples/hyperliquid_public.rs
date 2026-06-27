use std::time::Duration;

use dcex::exchanges::hyperliquid::HyperliquidClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = HyperliquidClient::public(false, Duration::from_secs(10))?;

    let meta = client.get_meta().await?;
    println!("{}", meta.data);

    let orderbook = client.get_l2book("BTC-USD-SWAP").await?;
    println!("{}", orderbook.data);

    Ok(())
}
