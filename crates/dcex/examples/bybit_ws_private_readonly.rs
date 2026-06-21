use std::env;
use std::time::Duration;

use dcex::ws::bybit::BybitPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("BYBIT_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("BYBIT_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = BybitPrivateWebSocket::new(api_key, api_secret, Duration::from_secs(10))?;
    ws.connect().await?;
    println!("{}", ws.recv().await?);
    ws.subscribe_wallet().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
