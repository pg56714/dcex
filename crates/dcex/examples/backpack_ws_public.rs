use std::time::Duration;

use dcex::ws::backpack::BackpackPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = BackpackPublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades("SOL_USDC").await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
