"""
Product table data fetching module.

This module provides synchronous functions to fetch product information from various
exchanges, used for building standardized product mapping tables.
"""

from dataclasses import asdict, dataclass

import polars as pl

from ..utils.common import Common
from ..utils.common_dataframe import to_dataframe
from ..utils.decimal_utils import reverse_decimal_places


@dataclass
class MarketInfo:
    """
    Market information data class.

    Used to store product information fetched from exchanges, including trading pairs,
    precision, minimum order sizes and other trading-related attributes.
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
    multiplier: str = "1"

    # contract
    size_per_contract: str = "1"

    def to_dict(self) -> dict[str, str]:
        """
        Convert MarketInfo instance to dictionary.

        Returns:
            dict[str, str]: Dictionary containing all fields
        """
        return asdict(self)


def binance() -> pl.DataFrame:
    """
    Fetch product information from Binance exchange.

    Returns:
        pl.DataFrame: DataFrame containing Binance product information
    """
    from ..binance._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)

    markets = []
    res_spot = market_http.get_spot_exchange_info()
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

    res_futures = market_http.get_futures_exchange_info()
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


def bitmart() -> pl.DataFrame:
    """
    Fetch product information from BitMart exchange.

    Returns:
        pl.DataFrame: DataFrame containing BitMart product information
    """
    from ..bitmart._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)

    markets = []
    res_swap = market_http.get_contracts_details()
    df_swap = to_dataframe(res_swap.get("data", {}).get("symbols", []))
    for market in df_swap.iter_rows(named=True):
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

    res_spot = market_http.get_trading_pairs_details()
    df_spot = to_dataframe(res_spot.get("data", {}).get("symbols", []))
    for market in df_spot.iter_rows(named=True):
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


def bitmex() -> pl.DataFrame:
    """
    Fetch product information from BitMEX exchange.

    Returns:
        pl.DataFrame: DataFrame containing BitMEX product information
    """
    from ..bitmex._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)

    res = market_http.get_instrument_info(filter={"state": ["FFWCSX", "FFCCSX", "IFXXXP"]})

    if not isinstance(res, list):
        res = []

    typ_map: dict[str, str] = {
        "FFWCSX": "swap",
        "FFCCSX": "futures",
        "IFXXXP": "spot",
    }

    markets = []
    for market in res:
        if not isinstance(market, dict):
            continue
        typ = market.get("typ")
        if not typ:
            continue
        product_type = typ_map.get(typ)
        if not product_type:
            continue

        symbol = market.get("symbol", "")
        base = market.get("underlying", "")
        quote = market.get("quoteCurrency", "")
        price_precision = str(market.get("tickSize", 0))
        size_precision = str(market.get("lotSize", 0))
        min_size = str(market.get("lotSize", 0))
        size_per_contract = str(market.get("multiplier", 1))
        min_notional = "0"

        if typ == "IFXXXP":
            product_symbol = f"{base}-{quote}-SPOT"
        elif typ == "FFWCSX":
            product_symbol = f"{base}-{quote}-SWAP"
        elif typ == "FFCCSX":
            if symbol and (base + quote) in symbol:
                expiry_str = symbol.replace(base + quote, "", 1)
            elif symbol:
                expiry_str = symbol.replace(base, "", 1)
            else:
                expiry_str = ""
            product_symbol = f"{base}-{quote}-{expiry_str}-SWAP"
        else:
            product_symbol = symbol or ""

        markets.append(
            MarketInfo(
                exchange=Common.BITMEX,
                exchange_symbol=symbol or "",
                product_symbol=product_symbol,
                product_type=product_type,
                exchange_type=typ or "",
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


def bybit() -> pl.DataFrame:
    """
    Fetch market information from Bybit exchange.

    Retrieves trading pairs from Bybit including linear futures, inverse futures,
    and spot markets. Standardizes the data into MarketInfo format.

    Returns:
        Polars DataFrame containing standardized market information from Bybit.
    """
    from ..bybit._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)

    markets = []
    linear_data = []
    cursor = None
    while True:
        res_linear = market_http.get_instruments_info(category="linear", cursor=cursor)
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
        res_inverse = market_http.get_instruments_info(category="inverse", cursor=cursor)
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
        res_spot = market_http.get_instruments_info(category="spot", cursor=cursor)
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


def gateio() -> pl.DataFrame:
    """
    Fetch product information from Gate.io exchange.

    Returns:
        pl.DataFrame: DataFrame containing Gate.io product information
    """
    from ..gateio._market_http import MarketHTTP

    market_http = MarketHTTP(preload_product_table=False)

    markets = []
    res_futures = market_http.get_all_futures_contracts()
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

    res_delivery = market_http.get_all_delivery_contracts()
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

    res_spot = market_http.get_spot_all_currency_pairs()
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


def okx() -> pl.DataFrame:
    """
    Fetch product information from OKX exchange.

    Returns:
        pl.DataFrame: DataFrame containing OKX product information
    """
    from ..okx._public_http import PublicHTTP

    public_http = PublicHTTP(preload_product_table=False)

    markets = []
    res_swap = public_http.get_public_instruments(instType="SWAP")
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

    res_spot = public_http.get_public_instruments(instType="SPOT")
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

    res_futures = public_http.get_public_instruments(instType="FUTURES")
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
