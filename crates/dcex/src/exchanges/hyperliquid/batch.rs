//! Fund movement and batch request implementations.

mod trade_operations {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::hyperliquid::client::HyperliquidClient;

    use crate::exchanges::hyperliquid::params::HyperliquidParams;
    use crate::exchanges::hyperliquid::trade::*;

    use crate::Result;

    impl HyperliquidClient {
        /// Places several orders in one `order` action, like hyperliquid-python-sdk `bulk_orders`.
        ///
        /// `orders` is a JSON array of objects using the `place_order` keys (`product_symbol`,
        /// `isBuy`, `price`, `size`, `reduceOnly`, `tif` or `isMarket`/`triggerPx`/`tpsl`,
        /// `cloid`). `grouping` applies to the whole action, so `normalTpsl`/`positionTpsl`
        /// can carry an entry order together with its TP/SL children.
        pub(in crate::exchanges::hyperliquid) async fn place_batch_orders_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            const BATCH_ORDER_FIELDS: &[&str] = &[
                "product_symbol",
                "isBuy",
                "price",
                "size",
                "reduceOnly",
                "tif",
                "isMarket",
                "triggerPx",
                "tpsl",
                "cloid",
            ];
            let orders = batch_items(params, "orders", BATCH_ORDER_FIELDS)?
                .iter()
                .map(|order| {
                    let reduce_only = order.optional_bool("reduceOnly")?.unwrap_or(false);
                    self.order_value_from_params(order, None, Some(reduce_only))
                })
                .collect::<Result<Vec<_>>>()?;
            let action = self.order_action(orders, params)?;
            self.submit_action(action, params).await
        }

        /// Cancels several orders by `oid` in one `cancel` action (SDK `bulk_cancel`).
        pub(in crate::exchanges::hyperliquid) async fn cancel_batch_orders_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            let cancels = batch_items(params, "cancels", &["product_symbol", "oid"])?
                .iter()
                .map(|cancel| {
                    Ok(object(vec![
                        (
                            "a",
                            uint(self.asset_id(cancel.required("product_symbol")?)?),
                        ),
                        ("o", uint(cancel.required_u64("oid")?)),
                    ]))
                })
                .collect::<Result<Vec<_>>>()?;
            let action = object(vec![
                ("type", string("cancel")),
                ("cancels", array(cancels)),
            ]);
            self.submit_action(action, params).await
        }

        /// Cancels several orders by `cloid` in one `cancelByCloid` action
        /// (SDK `bulk_cancel_by_cloid`).
        pub(in crate::exchanges::hyperliquid) async fn cancel_batch_orders_by_cloid_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            let cancels = batch_items(params, "cancels", &["product_symbol", "cloid"])?
                .iter()
                .map(|cancel| {
                    Ok(object(vec![
                        (
                            "asset",
                            uint(self.asset_id(cancel.required("product_symbol")?)?),
                        ),
                        ("cloid", string(&cancel.cloid("cloid")?)),
                    ]))
                })
                .collect::<Result<Vec<_>>>()?;
            let action = object(vec![
                ("type", string("cancelByCloid")),
                ("cancels", array(cancels)),
            ]);
            self.submit_action(action, params).await
        }

        pub(in crate::exchanges::hyperliquid) async fn modify_batch_orders_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            let modifies = normalize_batch_modifies(params.ordered_json_required("modifies")?)?;
            let action = object(vec![
                ("type", string("batchModify")),
                ("modifies", modifies),
            ]);
            self.submit_action(action, params).await
        }
    }
}

mod wrappers {
    use crate::exchanges::hyperliquid::HyperliquidClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; HyperliquidClient;
     public [

     ];
     private [
    cancel_batch_orders(cancels => "cancels"),
    cancel_batch_orders_by_cloid(cancels => "cancels"),
    modify_batch_orders(modifies => "modifies"),
    place_batch_orders(orders => "orders")
     ];
    }
}
