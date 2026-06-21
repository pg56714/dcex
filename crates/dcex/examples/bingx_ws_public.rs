use std::time::Duration;

use dcex::ws::bingx::BingxPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = BingxPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC-USDT-SPOT").await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
