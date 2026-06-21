use std::time::Duration;

use dcex::ws::kraken::KrakenPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = KrakenPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC-USD-SPOT").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
