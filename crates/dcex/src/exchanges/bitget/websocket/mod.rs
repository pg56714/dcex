mod private;
#[cfg(test)]
mod private_tests;
mod public;
mod trading;

pub use private::{BitgetPrivateWebSocket, BitgetPrivateWebSocketArg};
pub use public::{BitgetPublicWebSocket, BitgetWebSocketArg};
