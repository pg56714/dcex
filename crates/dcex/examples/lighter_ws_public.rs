use std::time::Duration;

use dcex::exchanges::lighter::chains::LighterNetwork;
use dcex::ws::lighter::LighterPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws =
        LighterPublicWebSocket::with_network(LighterNetwork::Mainnet, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades(0).await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
