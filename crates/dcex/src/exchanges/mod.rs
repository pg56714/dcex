macro_rules! impl_exchange_method_wrappers {
    (
        $client:ty;
        public [$($public_method:ident($($public_param:ident => $public_key:literal),*) => $public_method_with:ident),* $(,)?];
        private [$($private_method:ident($($private_param:ident => $private_key:literal),*) => $private_method_with:ident),* $(,)?] $(;)?
    ) => {
        impl $client {
            $(
                pub async fn $public_method(
                    &self,
                    $($public_param: impl ToString),*
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    let params = vec![$(($public_key.to_string(), $public_param.to_string())),*];
                    self.$public_method_with(params).await
                }

                pub async fn $public_method_with(
                    &self,
                    params: Vec<(String, String)>,
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    self.public_request(stringify!($public_method), params).await
                }
            )*

            $(
                pub async fn $private_method(
                    &self,
                    $($private_param: impl ToString),*
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    let params = vec![$(($private_key.to_string(), $private_param.to_string())),*];
                    self.$private_method_with(params).await
                }

                pub async fn $private_method_with(
                    &self,
                    params: Vec<(String, String)>,
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    self.private_request(stringify!($private_method), params).await
                }
            )*
        }
    };
}

pub(crate) use impl_exchange_method_wrappers;

pub mod aster;
pub mod backpack;
pub mod binance;
pub mod bingx;
pub mod bitget;
pub mod bitmart;
pub mod bitmex;
pub mod bybit;
pub mod gateio;
pub mod hyperliquid;
pub mod kraken;
pub mod kucoin;
pub mod lighter;
pub mod mexc;
pub mod okx;
