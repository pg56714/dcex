use std::time::Duration;

use dcex::exchanges::lighter::LighterNetwork;
use dcex::ws::lighter::LighterPrivateWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    tokio::try_join!(
        read_network(LighterNetwork::Mainnet),
        read_network(LighterNetwork::Robinhood),
    )?;
    Ok(())
}

async fn read_network(network: LighterNetwork) -> dcex::Result<()> {
    let mut ws = LighterPrivateWebSocket::with_env_credentials(network, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_account_all_orders().await?;
    println!("{network}: {}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
