# ruff: noqa: ANN401
"""Arcus HTTP implementation mixins."""

import json
from collections.abc import Mapping
from typing import Any

from ._http_manager import HTTPManager, SpotHTTPManager
from ._request_params import _params


class TradeHTTP(HTTPManager):
    """Arcus perpetual trade methods."""

    def sign_websocket_request(
        self, request_id: int, method_name: str, **params: object
    ) -> dict[str, Any]:
        """
        Build a signed WS frame using the named REST method and its parameters.

        Does not submit an order. May fetch public market metadata for tick/step
        conversion. Batch fields (orders, cancels, modifies) accept lists.
        """
        encoded = {
            k: json.dumps(v, allow_nan=False) if isinstance(v, (list, dict)) else v
            for k, v in params.items()
        }
        result = json.loads(
            self._native_client.sign_websocket_request(request_id, method_name, _params(**encoded))
        )
        if not isinstance(result, dict):
            raise TypeError("Unexpected Arcus signed WebSocket frame")
        return result

    def cancel_all_orders(
        self, product_symbol: str | None = None, valid_until: int | None = None
    ) -> Any:  # noqa: ANN401
        """Request cancel-all for this account, optionally limited to a market."""
        return self.private_request(
            "cancel_all_orders", product_symbol=product_symbol, valid_until=valid_until
        )

    def schedule_cancel(self, time: int, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Arm or refresh a cancel-all deadline (absolute epoch microseconds)."""
        return self.private_request("schedule_cancel", time=time, product_symbol=product_symbol)

    def disarm_scheduled_cancel(self, product_symbol: str | None = None) -> Any:  # noqa: ANN401
        """Disarm the account-wide or market-scoped cancel-all deadline."""
        return self.private_request("disarm_scheduled_cancel", product_symbol=product_symbol)

    def place_order(
        self,
        product_symbol: str,
        side: str,
        price: str,
        quantity: str,
        *,
        order_type: str = "LIMIT",
        time_in_force: str = "GTT",
        good_til_time: int | None = None,
        reduce_only: bool = False,
        client_order_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Submit an order; REST 200/202 is acknowledgement, not a confirmed fill."""
        return self.private_request(
            "place_order",
            product_symbol=product_symbol,
            side=side,
            price=price,
            quantity=quantity,
            order_type=order_type,
            time_in_force=time_in_force,
            good_til_time=good_til_time,
            reduce_only=reduce_only,
            client_order_id=client_order_id,
        )

    def modify_order(
        self,
        product_symbol: str,
        side: str,
        price: str,
        quantity: str,
        good_til_time: int,
        time_in_force: str,
        reduce_only: bool,
        *,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Modify one Perps order by server or client ID; acknowledgement is not a fill."""
        return self.private_request(
            "modify_order",
            product_symbol=product_symbol,
            side=side,
            price=price,
            quantity=quantity,
            good_til_time=good_til_time,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            order_id=order_id,
            client_order_id=client_order_id,
        )

    def cancel_order(self, product_symbol: str, order_id: str) -> Any:  # noqa: ANN401
        """Submit an order cancellation."""
        return self.private_request(
            "cancel_order", product_symbol=product_symbol, order_id=order_id
        )


class SpotTradeHTTP(SpotHTTPManager):
    """Arcus spot trade methods."""

    def build_signed_quote(
        self,
        quote: Mapping[str, Any],
        taker: str,
        signature: str,
        *,
        permits: list[Mapping[str, Any]] | None = None,
        route_tag: str | None = None,
        builder_fee_bps: int | None = None,
    ) -> dict[str, Any]:
        """Build a validated submit body from an externally signed firm quote."""
        return self._native_client.build_signed_quote_json(
            json.dumps(dict(quote), separators=(",", ":")),
            taker,
            signature,
            None if permits is None else json.dumps(permits, separators=(",", ":")),
            route_tag,
            builder_fee_bps,
        )

    def submit_signed_quote(self, signed_quote: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a wallet-signed Arcus quote; this can execute a real spot trade."""
        return self._call(
            "private_request",
            "submit_signed_quote",
            [("signed_quote_json", json.dumps(dict(signed_quote), separators=(",", ":")))],
        )
