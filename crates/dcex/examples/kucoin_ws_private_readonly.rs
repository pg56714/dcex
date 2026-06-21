use std::env;
use std::time::Duration;

use dcex::ws::kucoin::KucoinPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("KUCOIN_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("KUCOIN_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let passphrase = env::var("KUCOIN_API_PASSPHRASE")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws =
        KucoinPrivateWebSocket::new(api_key, api_secret, passphrase, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_orders().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
