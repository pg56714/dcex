use std::env;
use std::time::Duration;

use dcex::ws::backpack::BackpackPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = env::var("BACKPACK_API_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let api_secret = env::var("BACKPACK_API_SECRET")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = BackpackPrivateWebSocket::new(api_key, api_secret, 5000, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_orders(None).await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
