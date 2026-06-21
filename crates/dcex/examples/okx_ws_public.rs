use std::time::Duration;

use dcex::ws::okx::OkxPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = OkxPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC-USDT-SPOT").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
