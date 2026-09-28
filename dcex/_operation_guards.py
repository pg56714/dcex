"""Validate local confirmation and account-wide scope before native dispatch."""


def require_confirmation(confirm: bool) -> None:
    """Require the literal boolean True for an explicitly confirmed operation."""
    if confirm is not True:
        raise ValueError("confirm=True is required for this account operation")


def require_scope(
    scope: object, all_symbols: bool, *, flag: str = "all_symbols", order_ids: object = None
) -> None:
    """Require either a nonempty scope or an explicit request for everything."""
    if type(all_symbols) is not bool:
        raise ValueError(f"{flag} must be a boolean")
    if isinstance(scope, list):
        has_scope = bool(scope) and all(isinstance(v, str) and bool(v.strip()) for v in scope)
    else:
        has_scope = isinstance(scope, str) and bool(scope.strip())
    if isinstance(order_ids, str):
        has_ids = bool(order_ids.strip()) and all(value.strip() for value in order_ids.split(","))
    elif isinstance(order_ids, list):
        has_ids = bool(order_ids) and all(
            isinstance(item, dict)
            and any(
                isinstance(item.get(key), str) and item[key].strip()
                for key in ("orderId", "clientOid")
            )
            for item in order_ids
        )
    else:
        has_ids = False
    if (has_scope or has_ids) == all_symbols:
        raise ValueError(f"provide a nonempty scope or {flag}=True, exclusively")
