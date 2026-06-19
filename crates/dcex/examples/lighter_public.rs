use std::time::Duration;

use dcex::exchanges::lighter::LighterClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = LighterClient::new(Duration::from_secs(10))?;

    let details = client.get_order_book_details(Vec::new()).await?;
    println!("{}", details.data);

    let status = client.get_status(Vec::new()).await?;
    println!("{}", status.data);

    Ok(())
}
