use std::env;
use std::time::Duration;

use dcex::ws::lighter::LighterPrivateWebSocket;

fn env_u64(name: &str) -> dcex::Result<u64> {
    let value = env::var(name).map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;
    value
        .parse::<u64>()
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))
}

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let account_index = env_u64("LIGHTER_ACCOUNT_INDEX")?;
    let api_key_index = env_u64("LIGHTER_API_KEY_INDEX")?;
    let api_private_key = env::var("LIGHTER_API_PRIVATE_KEY")
        .map_err(|error| dcex::DcexError::InvalidInput(error.to_string()))?;

    let mut ws = LighterPrivateWebSocket::new(
        account_index,
        api_key_index,
        api_private_key,
        false,
        Duration::from_secs(10),
    )?;
    ws.connect().await?;
    ws.subscribe_account_all_orders().await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
