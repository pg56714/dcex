use std::time::Duration;

use dcex::exchanges::hyperliquid::HyperliquidClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = HyperliquidClient::new(false, None, None, Duration::from_secs(10))?;

    let meta = client.public_request("get_meta", Vec::new()).await?;
    println!("{}", meta.data);

    let orderbook = client
        .public_request(
            "get_l2book",
            vec![("product_symbol".to_string(), "BTC-USD-SWAP".to_string())],
        )
        .await?;
    println!("{}", orderbook.data);

    Ok(())
}
