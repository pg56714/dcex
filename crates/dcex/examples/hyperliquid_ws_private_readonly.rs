use std::env;
use std::time::Duration;

use dcex::ws::hyperliquid::HyperliquidPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let user = env::var("HYPERLIQUID_USER_ADDRESS")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = HyperliquidPrivateWebSocket::new(user, false, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_user_events().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
