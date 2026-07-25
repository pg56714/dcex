use std::time::Duration;

use dcex::ws::mexc::MexcPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = MexcPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("BTC-USDT-SPOT", "100ms").await?;
    println!("{}", String::from_utf8_lossy(&ws.recv().await?));
    ws.close().await?;
    Ok(())
}
