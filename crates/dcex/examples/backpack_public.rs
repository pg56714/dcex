use std::time::Duration;

use dcex::exchanges::backpack::BackpackClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BackpackClient::new(None, None, 5_000, Duration::from_secs(10))?;
    let markets = client.get_markets(Vec::new()).await?;
    println!("{}", markets.data);
    Ok(())
}
