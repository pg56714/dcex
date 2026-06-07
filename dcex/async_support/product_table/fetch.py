"""
Product table fetch module for retrieving market information from various exchanges.

This module provides functions to fetch market data from different cryptocurrency exchanges
and standardize the information into a common format using the MarketInfo dataclass.
"""

from dataclasses import asdict, dataclass

import polars as pl

from ...utils.common import Common
from ...utils.common_dataframe import to_dataframe
from ...utils.decimal_utils import reverse_decimal_places


@dataclass
class MarketInfo:
    """
    Data class representing standardized market information from exchanges.

    This class provides a common structure for storing market data across different
    cryptocurrency exchanges, including trading pairs, precision settings, and
    minimum order requirements.

    Attributes:
        exchange: Name of the exchange (e.g., "BINANCE", "OKX").
        exchange_symbol: Symbol used by the exchange for this product.
        product_symbol: Standardized product symbol used internally.
        product_type: Type of product (e.g., "spot", "swap", "futures").
        exchange_type: Exchange-specific product type.
        price_precision: Decimal precision for price values.
        size_precision: Decimal precision for order sizes.
        min_size: Minimum order size allowed.
        base_currency: Base currency of the trading pair.
        quote_currency: Quote currency of the trading pair.
        min_notional: Minimum notional value for orders.
        size_per_contract: Size per contract for derivatives.
    """

    exchange: str
    exchange_symbol: str
    product_symbol: str
    product_type: str
    exchange_type: str
    price_precision: str
    size_precision: str
    min_size: str
    base_currency: str = ""
    quote_currency: str = ""
    min_notional: str = "0"

    # contract
    size_per_contract: str = "1"

    def to_dict(self) -> dict[str, str]:
        """
        Convert MarketInfo instance to dictionary.

        Returns:
            Dictionary representation of the MarketInfo instance.
        """
        return asdict(self)


async def binance() -> pl.DataFrame:
    """
    Fetch market information from Binance exchange.

    Retrieves trading pairs from Binance including spot and futures markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Binance.
    """
    from ..binance._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_spot = await market_http.get_spot_exchange_info()
    df_spot = to_dataframe(res_spot.get("symbols", []))
    for market in df_spot.iter_rows(named=True):
        base = market["baseAsset"]
        quote = market["quoteAsset"]
        product_symbol = f"{base}-{quote}-SPOT"

        price_filter = next((f for f in market["filters"] if f["filterType"] == "PRICE_FILTER"), {})
        lot_size_filter = next((f for f in market["filters"] if f["filterType"] == "LOT_SIZE"), {})
        min_notional_filter = next(
            (f for f in market["filters"] if f["filterType"] == "NOTIONAL"), {}
        )

        markets.append(
            MarketInfo(
                exchange=Common.BINANCE,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="spot",
                exchange_type="spot",
                base_currency=market["baseAsset"],
                quote_currency=market["quoteAsset"],
                price_precision=price_filter.get("tickSize", "0"),
                size_precision=lot_size_filter.get("stepSize", "0"),
                min_size=lot_size_filter.get("minQty", "0"),
                min_notional=str(float(min_notional_filter.get("minNotional", "0"))),
            )
        )

    res_futures = await market_http.get_futures_exchange_info()
    df_futures = to_dataframe(res_futures.get("symbols", []))
    for market in df_futures.iter_rows(named=True):
        base = market["baseAsset"]
        quote = market["quoteAsset"]

        parts = market["symbol"].split("_")
        if len(parts) >= 2:
            expiry_str = parts[1]
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"
        else:
            product_symbol = f"{base}-{quote}-SWAP"

        price_filter = next((f for f in market["filters"] if f["filterType"] == "PRICE_FILTER"), {})
        lot_size_filter = next((f for f in market["filters"] if f["filterType"] == "LOT_SIZE"), {})
        min_notional_filter = next(
            (f for f in market["filters"] if f["filterType"] == "MIN_NOTIONAL"), {}
        )

        markets.append(
            MarketInfo(
                exchange=Common.BINANCE,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="swap",
                exchange_type=market["contractType"],
                base_currency=base,
                quote_currency=quote,
                price_precision=price_filter.get("tickSize", "0"),
                size_precision=lot_size_filter.get("stepSize", "0"),
                min_size=lot_size_filter.get("minQty", "0"),
                min_notional=min_notional_filter.get("notional", "0"),
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def bingx() -> pl.DataFrame:
    """
    Fetch market information from BingX exchange.

    Retrieves trading pairs from BingX including spot and swap markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from BingX.
    """
    from ..bingx._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res = await market_http.get_swap_instrument_info()
    for market in res.get("data", []):
        if not isinstance(market, dict):
            continue
        symbol = market["symbol"]
        base, quote = symbol.rsplit("-", 1)

        product_symbol = f"{base}-{quote}-SWAP"

        price_precision_val = int(market.get("pricePrecision", 0))
        quantity_precision_val = int(market.get("quantityPrecision", 0))

        price_precision = (
            str(reverse_decimal_places(price_precision_val)) if price_precision_val > 0 else "0"
        )
        size_precision = (
            str(reverse_decimal_places(quantity_precision_val))
            if quantity_precision_val > 0
            else "0"
        )
        min_size = size_precision

        markets.append(
            MarketInfo(
                exchange=Common.BINGX,
                exchange_symbol=symbol,
                product_symbol=product_symbol,
                product_type="swap",
                exchange_type="perpetual",
                base_currency=base,
                quote_currency=quote,
                price_precision=price_precision,
                size_precision=size_precision,
                min_size=min_size,
                min_notional=str(market.get("tradeMinUSDT", "0")),
                size_per_contract=str(market.get("size", "1")),
            )
        )

    res_spot = await market_http.get_spot_instrument_info()
    spot_data = res_spot.get("data", {})
    spot_symbols = spot_data.get("symbols", spot_data) if isinstance(spot_data, dict) else spot_data
    for market in spot_symbols:
        if not isinstance(market, dict):
            continue
        symbol = market["symbol"]
        base, quote = symbol.rsplit("-", 1)

        markets.append(
            MarketInfo(
                exchange=Common.BINGX,
                exchange_symbol=symbol,
                product_symbol=f"{base}-{quote}-SPOT",
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=str(market.get("tickSize", "0")),
                size_precision=str(market.get("stepSize", "0")),
                min_size=str(market.get("minQty", "0")),
                min_notional=str(market.get("minNotional", "0")),
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def bitget() -> pl.DataFrame:
    """
    Fetch market information from Bitget exchange.

    Retrieves trading pairs from Bitget including spot and USDT-M futures markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Bitget.
    """
    from ..bitget._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_spot = await market_http.get_spot_symbols()
    for market in res_spot.get("data", []):
        if not isinstance(market, dict):
            continue
        status = str(market.get("status", "")).lower()
        if status and status != "online":
            continue

        base = str(market["baseCoin"])
        quote = str(market["quoteCoin"])
        price_precision = int(str(market.get("pricePrecision", "0") or "0"))
        quantity_precision = int(str(market.get("quantityPrecision", "0") or "0"))

        markets.append(
            MarketInfo(
                exchange=Common.BITGET,
                exchange_symbol=str(market["symbol"]),
                product_symbol=f"{base}-{quote}-SPOT",
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=str(reverse_decimal_places(price_precision)),
                size_precision=str(reverse_decimal_places(quantity_precision)),
                min_size=str(market.get("minTradeAmount", "0")),
                min_notional=str(market.get("minTradeUSDT", "0")),
            )
        )

    res_futures = await market_http.get_futures_contracts(productType="USDT-FUTURES")
    for market in res_futures.get("data", []):
        if not isinstance(market, dict):
            continue
        status = str(market.get("symbolStatus") or market.get("status") or "").lower()
        if status and status not in {"normal", "online"}:
            continue

        base = str(market["baseCoin"])
        quote = str(market["quoteCoin"])
        price_precision = int(str(market.get("pricePlace", "0") or "0"))
        volume_precision = int(str(market.get("volumePlace", "0") or "0"))

        markets.append(
            MarketInfo(
                exchange=Common.BITGET,
                exchange_symbol=str(market["symbol"]),
                product_symbol=f"{base}-{quote}-SWAP",
                product_type="swap",
                exchange_type=str(market.get("symbolType", "USDT-FUTURES")),
                base_currency=base,
                quote_currency=quote,
                price_precision=str(reverse_decimal_places(price_precision)),
                size_precision=str(reverse_decimal_places(volume_precision)),
                min_size=str(market.get("minTradeNum", "0")),
                min_notional=str(market.get("minTradeUSDT", "0")),
                size_per_contract=str(market.get("sizeMultiplier", "1")),
            )
        )

    markets = [market.to_dict() for market in markets]
    await market_http.close()
    return pl.DataFrame(markets)


async def bitmart() -> pl.DataFrame:
    """
    Fetch market information from BitMart exchange.

    Retrieves trading pairs from BitMart including swap and spot markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from BitMart.
    """
    from ..bitmart._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_swap = await market_http.get_contracts_details()
    for market in res_swap.get("data", {}).get("symbols", []):
        if not isinstance(market, dict):
            continue

        base = market["base_currency"]
        quote = market["quote_currency"]
        product_symbol = f"{base}-{quote}-SWAP"

        markets.append(
            MarketInfo(
                exchange=Common.BITMART,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="swap",
                exchange_type="swap",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["price_precision"],
                size_precision=market["vol_precision"],
                min_size=market["min_volume"],
                size_per_contract=market["contract_size"],
            )
        )

    res_spot = await market_http.get_trading_pairs_details()
    for market in res_spot.get("data", {}).get("symbols", []):
        if not isinstance(market, dict):
            continue

        base = market["base_currency"]
        quote = market["quote_currency"]
        product_symbol = f"{base}-{quote}-SPOT"

        markets.append(
            MarketInfo(
                exchange=Common.BITMART,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=str(reverse_decimal_places(market["price_max_precision"])),
                size_precision=market["quote_increment"],
                min_size=market["base_min_size"],
                min_notional=market["min_buy_amount"],
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def bitmex() -> pl.DataFrame:
    """
    Fetch market information from BitMEX exchange.

    Retrieves trading pairs from BitMEX including swap, futures, and spot markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from BitMEX.
    """
    from ..bitmex._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    res = await market_http.get_instrument_info(
        filter={"typ": ["FFWCSX", "FFCCSX", "IFXXXP"]},
        count=500,
    )

    if not isinstance(res, list):
        res = []

    typ_map = {
        "FFWCSX": "swap",
        "FFCCSX": "futures",
        "IFXXXP": "spot",
    }

    markets = []
    for market in res:
        if not isinstance(market, dict):
            continue

        typ = market.get("typ", "")
        product_type = typ_map.get(typ)
        if not product_type:
            continue

        symbol = market["symbol"]
        base = market.get("underlying", "")
        quote = market["quoteCurrency"]
        price_precision = str(market["tickSize"])
        size_precision = str(market["lotSize"])
        min_size = str(market["lotSize"])
        size_per_contract = str(market["multiplier"])
        min_notional = "0"

        if typ == "IFXXXP":
            product_symbol = f"{base}-{quote}-SPOT"
        elif typ == "FFWCSX":
            product_symbol = f"{base}-{quote}-SWAP"
        elif typ == "FFCCSX":
            if (base + quote) in symbol:
                expiry_str = symbol.replace(base + quote, "", 1)
            else:
                expiry_str = symbol.replace(base, "", 1)
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"
        else:
            product_symbol = symbol

        markets.append(
            MarketInfo(
                exchange=Common.BITMEX,
                exchange_symbol=symbol,
                product_symbol=product_symbol,
                product_type=product_type,
                exchange_type=typ,
                base_currency=base,
                quote_currency=quote,
                price_precision=price_precision,
                size_precision=size_precision,
                min_size=min_size,
                min_notional=min_notional,
                size_per_contract=size_per_contract,
            ).to_dict()
        )

    return pl.DataFrame(markets)


async def bybit() -> pl.DataFrame:
    """
    Fetch market information from Bybit exchange.

    Retrieves trading pairs from Bybit including linear futures, inverse futures,
    and spot markets. Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Bybit.
    """
    from ..bybit._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    linear_data = []
    cursor = None
    while True:
        res_linear = await market_http.get_instruments_info(category="linear", cursor=cursor)
        if "list" in res_linear.get("result", {}):
            linear_data.extend(res_linear["result"]["list"])
        result = res_linear.get("result", {})
        if result.get("nextPageCursor", "") == "":
            break
        cursor = result["nextPageCursor"]

    df_linear = to_dataframe(linear_data)
    for market in df_linear.iter_rows(named=True):
        base = market["baseCoin"]
        quote = market["quoteCoin"]

        parts = market["symbol"].split("-")
        if len(parts) >= 2:
            expiry_str = parts[1]
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"
        else:
            product_symbol = f"{base}-{quote}-SWAP"

        if market["contractType"] == "LinearFutures":
            product_type = "futures"
        else:
            product_type = "swap"

        markets.append(
            MarketInfo(
                exchange=Common.BYBIT,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type=product_type,
                exchange_type="linear",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["priceFilter"]["tickSize"],
                size_precision=market["lotSizeFilter"]["qtyStep"],
                min_size=market["lotSizeFilter"]["minOrderQty"],
                min_notional=market["lotSizeFilter"].get("minNotionalValue", "0"),
            )
        )

    inverse_data = []
    cursor = None
    while True:
        res_inverse = await market_http.get_instruments_info(category="inverse", cursor=cursor)
        if "list" in res_inverse.get("result", {}):
            inverse_data.extend(res_inverse["result"]["list"])
        result = res_inverse.get("result", {})
        if result.get("nextPageCursor", "") == "":
            break
        cursor = result["nextPageCursor"]

    df_inverse = to_dataframe(inverse_data)
    for market in df_inverse.iter_rows(named=True):
        base = market["baseCoin"]
        quote = market["quoteCoin"]

        parts = market["symbol"].split("-")
        if len(parts) >= 2:
            base, expiry_str = parts[0], parts[1]
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"
        else:
            product_symbol = f"{base}-{quote}-SWAP"

        if market["contractType"] == "LinearFutures":
            product_type = "futures"
        else:
            product_type = "swap"

        markets.append(
            MarketInfo(
                exchange=Common.BYBIT,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type=product_type,
                exchange_type="inverse",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["priceFilter"]["tickSize"],
                size_precision=market["lotSizeFilter"]["qtyStep"],
                min_size=market["lotSizeFilter"]["minOrderQty"],
            )
        )

    spot_data = []
    cursor = None
    while True:
        res_spot = await market_http.get_instruments_info(category="spot", cursor=cursor)
        if "list" in res_spot.get("result", {}):
            spot_data.extend(res_spot["result"]["list"])
        result = res_spot.get("result", {})
        if result.get("nextPageCursor", "") == "":
            break
        cursor = result["nextPageCursor"]

    df_spot = to_dataframe(spot_data)
    for market in df_spot.iter_rows(named=True):
        base = market["baseCoin"]
        quote = market["quoteCoin"]
        product_symbol = f"{base}-{quote}-SPOT"

        markets.append(
            MarketInfo(
                exchange=Common.BYBIT,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["priceFilter"]["tickSize"],
                size_precision=market["lotSizeFilter"]["basePrecision"],
                min_size=market["lotSizeFilter"]["minOrderQty"],
                min_notional=market["lotSizeFilter"].get("minNotionalValue", "0"),
            )
        )
    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def gateio() -> pl.DataFrame:
    """
    Fetch market information from Gate.io exchange.

    Retrieves trading pairs from Gate.io including futures, delivery contracts,
    and spot markets. Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Gate.io.
    """
    from ..gateio._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_futures = await market_http.get_all_futures_contracts()
    df_futures = to_dataframe(res_futures)
    for market in df_futures.iter_rows(named=True):
        parts = market["name"].split("_")
        if len(parts) == 2:
            base, quote = parts[0], parts[1]
            product_symbol = f"{base}-{quote}-SWAP"
        elif len(parts) == 3:
            base, quote, expiry_str = parts[0], parts[1], parts[2]
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"

        markets.append(
            MarketInfo(
                exchange=Common.GATEIO,
                exchange_symbol=market["name"],
                product_symbol=product_symbol,
                product_type="swap",
                exchange_type="futures",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["order_price_round"],
                size_precision=str(market["order_size_min"]),
                min_size=str(market["order_size_min"]),
                size_per_contract=market["quanto_multiplier"],
            )
        )

    res_delivery = await market_http.get_all_delivery_contracts()
    df_deliver = to_dataframe(res_delivery)
    for market in df_deliver.iter_rows(named=True):
        parts = market["name"].split("_")
        if len(parts) == 2:
            base, quote = parts[0], parts[1]
            product_symbol = f"{base}-{quote}-SWAP"
        elif len(parts) == 3:
            base, quote, expiry_str = parts[0], parts[1], parts[2]
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"

        markets.append(
            MarketInfo(
                exchange=Common.GATEIO,
                exchange_symbol=market["name"],
                product_symbol=product_symbol,
                product_type="futures",
                exchange_type="delivery",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["order_price_round"],
                size_precision=str(market["order_size_min"]),
                min_size=str(market["order_size_min"]),
                size_per_contract=market["quanto_multiplier"],
            )
        )

    res_spot = await market_http.get_spot_all_currency_pairs()
    df_spot = to_dataframe(res_spot)
    for market in df_spot.iter_rows(named=True):
        base = market["base"]
        quote = market["quote"]
        product_symbol = f"{base}-{quote}-SPOT"

        markets.append(
            MarketInfo(
                exchange=Common.GATEIO,
                exchange_symbol=market["id"],
                product_symbol=product_symbol,
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=str(reverse_decimal_places(market["precision"])),
                size_precision=str(reverse_decimal_places(market["amount_precision"])),
                min_size=market["min_base_amount"],
                min_notional=market["min_quote_amount"],
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def hyperliquid() -> pl.DataFrame:
    """
    Fetch market information from Hyperliquid exchange.

    Retrieves trading pairs from Hyperliquid including perpetual swaps and spot markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Hyperliquid.
    """
    from ..hyperliquid._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_prep = await market_http.get_meta()
    df_prep = to_dataframe(res_prep.get("universe", []))

    for idx, market in enumerate(df_prep.iter_rows(named=True)):
        coin = market["name"]
        tick = str(reverse_decimal_places(market["szDecimals"]))
        markets.append(
            MarketInfo(
                exchange=Common.HYPERLIQUID,
                exchange_symbol=f'["{coin}", {idx}]',
                product_symbol=f"{coin}-USD-SWAP",
                product_type="swap",
                exchange_type="perpetual",
                base_currency=coin,
                quote_currency="USD",
                price_precision=tick,
                size_precision=tick,
                min_size=tick,
            )
        )

    res_spot = await market_http.get_spot_meta()
    token_by_index = {
        token["index"]: token for token in res_spot.get("tokens", []) if isinstance(token, dict)
    }

    for idx, market in enumerate(res_spot.get("universe", [])):
        if not isinstance(market, dict):
            continue
        base_i, quote_i = market["tokens"]
        base_token = token_by_index.get(base_i)
        quote_token = token_by_index.get(quote_i)
        if base_token is None or quote_token is None:
            continue

        base = base_token["name"]  # e.g. "PURR"
        quote = quote_token["name"]  # e.g. "USDC"
        tick = str(reverse_decimal_places(base_token["szDecimals"]))
        asset_index = market.get("index", idx)

        markets.append(
            MarketInfo(
                exchange=Common.HYPERLIQUID,
                exchange_symbol='["{}", {}]'.format(market["name"], 10000 + asset_index),
                product_symbol=f"{base}-{quote}-SPOT",
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=tick,
                size_precision=tick,
                min_size=tick,
            )
        )
    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


def _normalize_kraken_currency(currency: str) -> str:
    aliases = {
        "XXBT": "BTC",
        "XBT": "BTC",
        "XDG": "DOGE",
        "ZUSD": "USD",
        "ZEUR": "EUR",
        "ZGBP": "GBP",
        "ZJPY": "JPY",
        "ZCAD": "CAD",
        "ZAUD": "AUD",
    }
    if currency in aliases:
        return aliases[currency]
    if currency.startswith(("X", "Z")) and len(currency) > 3:
        stripped = currency[1:]
        return aliases.get(stripped, stripped)
    return currency


def _kraken_size_precision(market: dict[str, object]) -> str:
    precision = int(str(market.get("contractValueTradePrecision", 0) or 0))
    return str(reverse_decimal_places(precision)) if precision > 0 else "1"


def _kraken_futures_product_symbol(
    symbol: str,
    base: str,
    quote: str,
    instrument_type: str,
    last_trading_time: object | None,
) -> tuple[str, str]:
    parts = symbol.split("_")
    prefix = parts[0] if parts else ""
    inverse_suffix = "-INVERSE" if instrument_type == "futures_inverse" else ""

    if last_trading_time:
        expiry = parts[2] if len(parts) > 2 else ""
        if expiry:
            return f"{base}-{quote}-{expiry}{inverse_suffix}-SWAP", "futures"
        return f"{base}-{quote}{inverse_suffix}-SWAP", "futures"

    if prefix in {"PI", "PF"}:
        return f"{base}-{quote}{inverse_suffix}-SWAP", "swap"

    return f"{base}-{quote}{inverse_suffix}-SWAP", "swap"


async def kucoin() -> pl.DataFrame:
    """
    Fetch market information from KuCoin exchange.

    Retrieves trading pairs from KuCoin including spot and futures markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from KuCoin.
    """
    from ..kucoin._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res = await market_http.get_spot_instrument_info()
    df = to_dataframe(res.get("data", []))

    for market in df.iter_rows(named=True):
        base = market["baseCurrency"]
        quote = market["quoteCurrency"]
        product_symbol = f"{base}-{quote}-SPOT"

        markets.append(
            MarketInfo(
                exchange=Common.KUCOIN,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=market["priceIncrement"],
                size_precision=market["baseIncrement"],
                min_size=market["baseMinSize"],
                min_notional=market["minFunds"] if market["minFunds"] else "0",
            )
        )

    res_futures = await market_http.get_futures_contracts()
    for market in res_futures.get("data", []):
        if not isinstance(market, dict):
            continue

        base = "BTC" if market["baseCurrency"] == "XBT" else str(market["baseCurrency"])
        quote = str(market["quoteCurrency"])
        product_symbol = f"{base}-{quote}-SWAP"

        markets.append(
            MarketInfo(
                exchange=Common.KUCOIN,
                exchange_symbol=market["symbol"],
                product_symbol=product_symbol,
                product_type="swap",
                exchange_type=market["type"],
                base_currency=base,
                quote_currency=quote,
                price_precision=str(market["tickSize"]),
                size_precision=str(market["lotSize"]),
                min_size=str(market["lotSize"]),
                size_per_contract=str(market["multiplier"]),
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def kraken() -> pl.DataFrame:
    """
    Fetch market information from Kraken exchange.

    Retrieves Kraken spot pairs and futures instruments, then standardizes them
    into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Kraken.
    """
    from ..kraken._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    markets = []
    res_spot = await market_http.get_spot_asset_pairs()
    for symbol, market in res_spot.get("result", {}).items():
        if not isinstance(market, dict):
            continue
        if market.get("status") and market.get("status") != "online":
            continue

        wsname = str(market.get("wsname", ""))
        if "/" in wsname:
            base, quote = [_normalize_kraken_currency(part) for part in wsname.split("/", 1)]
        else:
            base = _normalize_kraken_currency(str(market.get("base", "")))
            quote = _normalize_kraken_currency(str(market.get("quote", "")))

        markets.append(
            MarketInfo(
                exchange=Common.KRAKEN,
                exchange_symbol=str(symbol),
                product_symbol=f"{base}-{quote}-SPOT",
                product_type="spot",
                exchange_type="spot",
                base_currency=base,
                quote_currency=quote,
                price_precision=str(
                    market.get(
                        "tick_size",
                        reverse_decimal_places(int(market.get("pair_decimals", 0) or 0)),
                    )
                ),
                size_precision=str(reverse_decimal_places(int(market.get("lot_decimals", 0) or 0))),
                min_size=str(market.get("ordermin", "0")),
                min_notional=str(market.get("costmin", "0")),
            )
        )

    res_futures = await market_http.get_futures_instruments(
        contractType=["futures_inverse", "futures_vanilla", "flexible_futures"],
    )
    for market in res_futures.get("instruments", []):
        if not isinstance(market, dict):
            continue
        instrument_type = str(market.get("type", ""))
        if instrument_type == "options":
            continue
        if not market.get("tradeable", False) or market.get("isExpired", False):
            continue

        symbol = str(market["symbol"])
        base = _normalize_kraken_currency(str(market.get("base", "")))
        quote = _normalize_kraken_currency(str(market.get("quote", "")))
        product_symbol, product_type = _kraken_futures_product_symbol(
            symbol=symbol,
            base=base,
            quote=quote,
            instrument_type=instrument_type,
            last_trading_time=market.get("lastTradingTime"),
        )

        markets.append(
            MarketInfo(
                exchange=Common.KRAKEN,
                exchange_symbol=symbol,
                product_symbol=product_symbol,
                product_type=product_type,
                exchange_type=instrument_type,
                base_currency=base,
                quote_currency=quote,
                price_precision=str(market.get("tickSize", "0")),
                size_precision=_kraken_size_precision(market),
                min_size=_kraken_size_precision(market),
                size_per_contract=str(market.get("contractSize", "1")),
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def mexc() -> pl.DataFrame:
    """
    Fetch market information from MEXC exchange.

    Retrieves MEXC spot pairs and USDT-M perpetual contracts, then standardizes
    them into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from MEXC.
    """
    from ..mexc._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)
    await market_http.async_init()

    try:
        markets = []
        res_spot = await market_http.get_spot_exchange_info()
        if isinstance(res_spot, dict):
            spot_symbols = res_spot.get("symbols", [])
        else:
            spot_symbols = []
        for market in spot_symbols:
            if not isinstance(market, dict):
                continue
            status = str(market.get("status", ""))
            if status and status not in {"1", "TRADING"}:
                continue
            if market.get("isSpotTradingAllowed") is False:
                continue

            base = str(market["baseAsset"])
            quote = str(market["quoteAsset"])
            quote_precision = int(str(market.get("quotePrecision", "0") or "0"))

            markets.append(
                MarketInfo(
                    exchange=Common.MEXC,
                    exchange_symbol=str(market["symbol"]),
                    product_symbol=f"{base}-{quote}-SPOT",
                    product_type="spot",
                    exchange_type="spot",
                    base_currency=base,
                    quote_currency=quote,
                    price_precision=str(reverse_decimal_places(quote_precision)),
                    size_precision=str(market.get("baseSizePrecision", "0")),
                    min_size=str(market.get("baseSizePrecision", "0")),
                    min_notional=str(market.get("quoteAmountPrecision", "0")),
                )
            )

        res_contract = await market_http.get_contract_details()
        if isinstance(res_contract, dict):
            contract_data = res_contract.get("data", [])
        else:
            contract_data = []
        if isinstance(contract_data, dict):
            contract_data = [contract_data]
        for market in contract_data:
            if not isinstance(market, dict):
                continue
            if market.get("state") not in {0, "0", None}:
                continue
            if market.get("apiAllowed") is False:
                continue

            base = str(market["baseCoin"])
            quote = str(market["quoteCoin"])

            markets.append(
                MarketInfo(
                    exchange=Common.MEXC,
                    exchange_symbol=str(market["symbol"]),
                    product_symbol=f"{base}-{quote}-SWAP",
                    product_type="swap",
                    exchange_type="perpetual",
                    base_currency=base,
                    quote_currency=quote,
                    price_precision=str(market.get("priceUnit", "0")),
                    size_precision=str(market.get("volUnit", "0")),
                    min_size=str(market.get("minVol", "0")),
                    size_per_contract=str(market.get("contractSize", "1")),
                )
            )
    finally:
        await market_http.close()

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)


async def okx() -> pl.DataFrame:
    """
    Fetch market information from OKX exchange.

    Retrieves trading pairs from OKX including swap, spot, and futures markets.
    Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from OKX.
    """
    from ..okx._public_http import PublicHTTP

    public_http = PublicHTTP(preload_product_table=False)
    await public_http.async_init()

    markets = []
    res_swap = await public_http.get_public_instruments(instType="SWAP")
    df_swap = to_dataframe(res_swap["data"]) if "data" in res_swap else pl.DataFrame()
    for market in df_swap.iter_rows(named=True):
        parts = market["instId"].split("-")
        if len(parts) >= 2:
            base, quote = parts[0], parts[1]

        markets.append(
            MarketInfo(
                exchange=Common.OKX,
                exchange_symbol=market["instId"],
                product_symbol=market["instId"],
                product_type="swap",
                exchange_type=market["instType"],
                base_currency=base,
                quote_currency=quote,
                price_precision=market["tickSz"],
                size_precision=market["lotSz"],
                min_size=market["minSz"],
                size_per_contract=market["ctVal"],
            )
        )

    res_spot = await public_http.get_public_instruments(instType="SPOT")
    df_spot = to_dataframe(res_spot["data"]) if "data" in res_spot else pl.DataFrame()
    for market in df_spot.iter_rows(named=True):
        base = market["baseCcy"]
        quote = market["quoteCcy"]

        markets.append(
            MarketInfo(
                exchange=Common.OKX,
                exchange_symbol=market["instId"],
                product_symbol=market["instId"] + "-SPOT",
                product_type="spot",
                exchange_type=market["instType"],
                base_currency=base,
                quote_currency=quote,
                price_precision=market["tickSz"],
                size_precision=market["lotSz"],
                min_size=market["minSz"],
            )
        )

    res_futures = await public_http.get_public_instruments(instType="FUTURES")
    df_futures = to_dataframe(res_futures["data"]) if "data" in res_futures else pl.DataFrame()
    for market in df_futures.iter_rows(named=True):
        parts = market["instId"].split("-")
        if len(parts) >= 2:
            base, quote = parts[0], parts[1]

        markets.append(
            MarketInfo(
                exchange=Common.OKX,
                exchange_symbol=market["instId"],
                product_symbol=market["instId"],
                product_type="futures",
                exchange_type=market["instType"],
                base_currency=base,
                quote_currency=quote,
                price_precision=market["tickSz"],
                size_precision=market["lotSz"],
                min_size=market["minSz"],
            )
        )

    markets = [market.to_dict() for market in markets]
    return pl.DataFrame(markets)
