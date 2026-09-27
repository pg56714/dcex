# Endpoint coverage and verification

**English** | [繁體中文](endpoint-audit.zh_tw.md)

Reviewed: 2026-09-27 against the supplied 3,180-row report, official API documentation and current source. Scope includes ordinary market data, trading, accounts, same-account-family transfers, investment and risk controls.

[Searchable full table](endpoint-coverage.html) · [Per-row JSON and evidence](endpoint-coverage-ledger.json) · [Remaining items](endpoint-recheck.md) · [New method index](endpoint-methods.md)

## Coverage status

**Every row has a disposition; implementation is not complete.** Rows may duplicate or group operations and cannot be converted into an official endpoint coverage percentage.

| Status | Rows | Meaning |
| --- | ---: | --- |
| `implemented` | 2838 | Rust and Python sync/async wrapper and route evidence |
| `protocol` | 173 | Generic async WS protocol support, not dedicated coverage of every topic |
| `superseded` | 37 | Older route replaced by a current API; see row-level mapping |
| `excluded` | 111 | Excluded under the agreed scope |
| `unavailable` | 9 | Retired, under maintenance or without a usable documented interface |
| `blocked` | 10 | Required specification or eligibility remains unconfirmed |
| `partial` | 2 | Grouped row partly implemented with a documented gap |

## Exchanges and Python methods

Counts include public convenience methods, aliases and signing helpers, not official endpoints. Additions are relative to `d0bbf8b0`. Sync/async method-name sets were checked for equality.

| Exchange / official docs | Sync | Async | New | Implemented rows | Protocol rows | Blocked / partial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [binance](https://developers.binance.com/en/docs) | 645 | 645 | 335 | 645 | 12 | 0 / 1 |
| [bybit](https://bybit-exchange.github.io/docs/v5/intro) | 301 | 301 | 130 | 287 | 23 | 0 / 0 |
| [okx](https://www.okx.com/docs-v5/en/#overview-rest-authentication-making-requests) | 378 | 378 | 201 | 361 | 0 | 0 / 0 |
| [bitget](https://www.bitget.com/docs/catalog/classic-contract-market/classic-contract-market) | 400 | 400 | 261 | 380 | 19 | 0 / 0 |
| [bingx](https://github.com/BingX-API/api-ai-skills) | 169 | 169 | 79 | 149 | 11 | 1 / 0 |
| [kraken](https://docs.kraken.com/api-reference/) | 130 | 130 | 63 | 97 | 29 | 1 / 0 |
| [mexc](https://www.mexc.com/api-docs/spot-v3/introduction) | 156 | 156 | 35 | 128 | 26 | 0 / 0 |
| [kucoin](https://www.kucoin.com/docs-new/v2/rest/ua/get-announcements) | 311 | 311 | 194 | 292 | 4 | 1 / 0 |
| [hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) | 91 | 91 | 44 | 63 | 23 | 0 / 0 |
| [lighter](https://apidocs.lighter.xyz/) | 122 | 122 | 49 | 80 | 14 | 1 / 1 |
| [backpack](https://docs.backpack.exchange/#tag/Account) | 81 | 81 | 16 | 77 | 0 | 1 / 0 |
| [aster](https://github.com/asterdex/api-docs) | 135 | 135 | 46 | 107 | 2 | 5 / 0 |
| [extended](https://api.docs.extended.exchange/) | 64 | 64 | 22 | 47 | 3 | 0 / 0 |
| [ondo](https://docs.ondoperps.xyz/api-reference) | 77 | 77 | 5 | 70 | 3 | 0 / 0 |
| [arcus](https://docs.arcus.xyz/api-reference) | 58 | 58 | 31 | 55 | 4 | 0 / 0 |

## Main additions in this completion pass

- **Binance:** Subaccounts/account administration, deposit questionnaires/read-only history, PM Earn and isolated-margin enable/disable; multi-market WS profiles, COIN-M time and caller-token subscriptions.
- **Bybit / OKX / Bitget:** Loans, leveraged tokens and server time; grid, DCA, Signal, recurring/copy trading; UTA grid and Reality fundamentals.
- **Kraken / MEXC / KuCoin / BingX:** Kraken EditOrder, charts, market history and pool statistics; MEXC STP, subaccount keys, deposits and listen keys; KuCoin UTA/OES/OTC and read-only reconciliation.
- **Hyperliquid / Lighter:** Info queries, pools, staking and account abstraction; Lighter same-master transfers, leases, explorer, exports and maker-only API keys.
- **Backpack / Aster / Extended / Arcus:** Backpack vault/prediction/borrow-lend; Aster prediction; Extended charts/interest/vaults; Arcus api-meta and leaderboard.

## Binance WebSocket market selection

`dcex.ws.binance.PublicClient(profile=...)`:

| Profile | Base URL |
| --- | --- |
| `spot` (default) | `wss://stream.binance.com:9443/ws` |
| `futures_public`, `options_public` | `wss://fstream.binance.com/public/ws` |
| `futures_market`, `options_market` | `wss://fstream.binance.com/market/ws` |
| `coin_futures` | `wss://dstream.binance.com/ws` |

Futures depth/bookTicker use public; other market data use market on a separate connection. Options allow 200 subscriptions per connection. Pass official stream names to `subscribe([...])`. Rust uses `BinancePublicWebSocket::with_profile(profile, timeout)`.

`PrivateClient(profile=...)` supports `futures` (default), `coin_futures`, `options`, `portfolio_margin` and `margin_risk`. Rust uses `BinancePrivateWebSocket::with_profile(http_client, profile, timeout, base_url)`. Listen-key create/renew/delete are supported; callers must schedule `keep_alive()`. `margin_risk` only covers cross-margin risk events. For trading events, use `SpotApiClient.subscribe_user_data_listen_token(token)`. Margin token creation REST authentication remains unconfirmed; callers must obtain and resubscribe with a fresh token before expiration.

[USD-M stream docs](https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Connect) · [Margin token docs](https://developers.binance.com/en/docs/products/margin-trading/listen-token-data-stream)

## Limits and verification

<!-- VERIFICATION -->
Rust `cargo test --workspace --all-features`: **656 passed**, **53 live tests ignored**. The native extension was rebuilt and installed in the project virtual environment.

Python full collection: **12,818 unique tests**, assigned across eight disjoint groups with their union checked against the complete collection. The first run had 12,810 passes and eight incorrect test expectations (public Kraken authentication and Binance exception types). After correcting these expectations, all **315 affected Kraken/Binance tests passed**. A final binding adjustment preserved `ValueError` for empty Binance credentials; all **38 Binance WS tests passed** against that rebuilt extension. There are no outstanding failures from these runs.

Ruff lint and format checks passed for the 73 changed Python files; `pyright dcex` reported 0 errors and 0 warnings. Rust format, Git whitespace checks, the 3,180-row ledger totals and local documentation links passed validation.
<!-- /VERIFICATION -->

No live orders or account administration operations were submitted. Offline tests verify routes, verbs, parameters, signatures, WS messages and response handling; they do not establish live eligibility or availability.

- OKX SBE returns raw bytes without a built-in decoder.
- Lighter explorer accepts `explorer_base_url`; historical exports require authorization and never automatically pay a fee.
- Wallet-authorized operations retain caller-provided signatures; Arcus userPreferences DELETE requires caller-provided authentication headers.
- External withdrawal/control and MM/partner-only operations are excluded; read-only history is not blanket-excluded.

Source report SHA-256: `6479d7c578f35b2bd9b6a243c37b239dbea399f17054dbecd1edfe98ffd92e07`.
