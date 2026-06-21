use std::env;
use std::time::Duration;

use dcex::ws::bitmart::BitmartPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("BITMART_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("BITMART_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let memo = env::var("BITMART_MEMO")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = BitmartPrivateWebSocket::new(api_key, api_secret, memo, Duration::from_secs(10))?;
    ws.connect().await?;
    println!("{}", ws.recv().await?);
    ws.subscribe_balance().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
