"""Arcus native request parameter conversion."""

from dcex._schema_codec import normalize_params


def _params(**kwargs: object) -> list[tuple[str, str]]:
    kwargs = normalize_params(kwargs)
    return [
        (name, str(value).lower() if isinstance(value, bool) else str(value))
        for name, value in kwargs.items()
        if value is not None
    ]
