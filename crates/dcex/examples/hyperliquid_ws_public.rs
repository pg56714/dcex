use std::time::Duration;

use dcex::ws::hyperliquid::HyperliquidPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = HyperliquidPublicWebSocket::new(false, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
