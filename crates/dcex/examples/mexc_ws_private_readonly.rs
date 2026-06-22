use std::env;
use std::time::Duration;

use dcex::ws::mexc::MexcPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("MEXC_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("MEXC_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = MexcPrivateWebSocket::with_secret(api_key, api_secret, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.keep_alive().await?;
    ws.subscribe_account().await?;
    println!("{:?}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
