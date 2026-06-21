use std::time::Duration;

use dcex::exchanges::aster::AsterMarket;
use dcex::ws::aster::AsterPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = AsterPublicWebSocket::new(AsterMarket::Futures, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_agg_trades("BTC-USDT-SWAP").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
