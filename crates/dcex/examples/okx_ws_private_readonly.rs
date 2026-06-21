use std::env;
use std::time::Duration;

use dcex::ws::okx::OkxPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("OKX_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("OKX_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let passphrase = env::var("OKX_PASSPHRASE")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws =
        OkxPrivateWebSocket::new(api_key, api_secret, passphrase, Duration::from_secs(10))?;
    ws.connect().await?;
    println!("{}", ws.recv().await?);
    ws.subscribe_account(None).await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
