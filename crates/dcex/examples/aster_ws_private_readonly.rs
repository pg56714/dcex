use std::env;
use std::time::Duration;

use dcex::exchanges::aster::AsterMarket;
use dcex::ws::aster::AsterPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let user_address = env::var("ASTER_USER_ADDRESS")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let signer_address = env::var("ASTER_SIGNER_ADDRESS")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    let private_key = env::var("ASTER_PRIVATE_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = AsterPrivateWebSocket::new(
        Some(user_address),
        signer_address,
        private_key,
        AsterMarket::Futures,
        Duration::from_secs(10),
    )?;
    ws.connect().await?;
    ws.keep_alive().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
