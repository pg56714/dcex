use std::time::Duration;

use dcex::ws::bybit::BybitPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = BybitPublicWebSocket::new("spot", Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC-USDT-SPOT").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
