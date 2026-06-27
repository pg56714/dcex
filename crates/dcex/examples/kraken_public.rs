use std::time::Duration;

use dcex::exchanges::kraken::KrakenClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = KrakenClient::public(Duration::from_secs(10))?;
    let response = client
        .get_spot_ticker()
        .param("product_symbol", "BTC-USDT-SPOT")
        .await?;
    println!("{}", response.data);
    Ok(())
}
