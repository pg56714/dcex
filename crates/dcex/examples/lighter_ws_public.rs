use std::time::Duration;

use dcex::ws::lighter::LighterPublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = LighterPublicWebSocket::new(false, Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_trades(0).await?;
    println!("{}", ws.recv().await?);
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
