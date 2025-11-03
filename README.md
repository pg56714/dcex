# dcex - dex & cex trading library

**Important**: No default broker tags are set. You may manually specify a broker tag within function arguments if needed.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

> Originally created and maintained by the same contributor, this fork continues active development, building upon the original foundation with enhanced design, unified DEX + CEX support, and fixes for previously unresolved issues.

A high-performance and lightweight Python library for interacting with cryptocurrency exchanges. dcex offers full synchronous and asynchronous support across major exchanges, designed for speed, modularity, and ease of use.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/dcex)](https://badge.fury.io/py/dcex)

## 📦 Installation

```bash
pip install dcex
```

or use `uv` to manage the project:

```bash
uv add dcex
```

## 🚀 Quick Start

### Synchronous Usage

```python
import dcex

client = dcex.binance()

klines = client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
print(klines)
```

### Asynchronous Usage

```python
import os
import asyncio
import dcex.async_support as dcex
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

async def main():
    client = await dcex.binance(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET
    )

    try:
        result = await client.get_income_history()
        print(result)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 Supported Exchanges

| Exchange        | Sync Support | Async Support |
| --------------- | ------------ | ------------- |
| **Binance**     | ✅           | ✅            |
| **Bybit**       | ✅           | ✅            |
| **OKX**         | ✅           | ✅            |
| **BitMart**     | ✅           | ✅            |
| **BitMEX**      | ✅           | ✅            |
| **Gate.io**     | ✅           | ✅            |
| **Hyperliquid** | Testing      | Testing       |
| **BingX**       | Developing   | Developing    |
| **KuCoin**      | Developing   | Developing    |
| **Zoomex**      | Developing   | Developing    |

## 🔍 Key Features

- 📘 Product Table Manager for unifying trading instruments in different exchanges
- 🔁 Sync & Async API clients with identical interfaces
- ⚡ Optimized for low-latency, high-frequency trading

## What is Product Table Manager(ptm)?

Ptm is a utility that standardizes and unifies trading instrument metadata across different exchanges, making cross-exchange strategy development easier.

It is a table that contains the following columns:

| Column            | Description                                                                                                                                                                                                                |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| exchange          | The exchange name                                                                                                                                                                                                          |
| product_symbol    | The symbol we use to identify the product, it will be the same in different exchanges. For example, `BTC-USDT-SWAP` is the same product in Binance and Bybit, which named `BTCUSDT` in Binance and `BTC-USDT-SWAP` in OKX. |
| exchange_symbol   | The symbol that the exchange will actually used                                                                                                                                                                            |
| product_type      | The type we will use, e.g. `spot`, `inverse`, `swap`, `futures`                                                                                                                                                            |
| exchange_type     | The type the exchange will actually used, e.g. `linear`, `INVERSE`, `perp`... different exchanges have different types, pretty annoying...                                                                                 |
| base_symbol       | The base symbol, e.g. `BTC`                                                                                                                                                                                                |
| quote_symbol      | The quote symbol, e.g. `USDT`                                                                                                                                                                                              |
| price_precision   | The price precision, e.g. `0.000001`                                                                                                                                                                                       |
| size_precision    | The size precision, e.g. `0.000001`                                                                                                                                                                                        |
| min_size          | The minimum size, e.g. `0.000001`                                                                                                                                                                                          |
| min_notional      | The minimum notional, e.g. `0.000001`                                                                                                                                                                                      |
| multiplier        | The multiplier of the product, such symbol like `1000BONKUSDT` in Bybit will need to be multiplied by 1000 to get the actual size, if you are trading across spot and swap, you will need this                             |
| size_per_contract | The size per contract. Sometimes 1 contract is not the same as 1 unit in exchanges like OKX.                                                                                                                               |

## How to use Product Table Manager?

In most cases, we have handled the case, but if you have any specific use cases, you can use the `ptm` to get the information you want.

```python
from dcex.utils.common import Common
from dcex.product_table.manager import ProductTableManager

ptm = ProductTableManager.get_instance(Common.BINANCE)

product_symbol = ptm.get_product_symbol(
    exchange=Common.BINANCE,
    exchange_symbol="BTCUSDT",
    product_type="swap",
)

print(product_symbol)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/pg56714/dcex/issues).
- **Discussions**: Discuss ideas and share your thoughts on [GitHub Discussions](https://github.com/pg56714/dcex/discussions).

## 📜 Disclaimer

Cryptocurrency trading involves significant risk. This library is provided as-is without any warranty. Users are responsible for their own trading decisions and risk management.
