use std::time::Duration;

use dcex::exchanges::backpack::BackpackClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BackpackClient::public(5_000, Duration::from_secs(10))?;
    let markets = client.get_markets().await?;
    println!("{}", markets.data);
    Ok(())
}
