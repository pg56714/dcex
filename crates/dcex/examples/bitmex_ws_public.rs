use std::time::Duration;

use dcex::ws::bitmex::BitmexPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = BitmexPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("XBTUSD").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
