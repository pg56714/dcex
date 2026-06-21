use std::env;
use std::time::Duration;

use dcex::ws::kraken::KrakenPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("KRAKEN_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("KRAKEN_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = KrakenPrivateWebSocket::new(api_key, api_secret, Duration::from_secs(10))?;
    let token = ws.connect().await?;
    println!("token={token}");
    ws.subscribe_balances().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
