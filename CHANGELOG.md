## 0.26.1 (2026-06-29)

### Fix

- send bingx unsigned json body
- align native params and timeout validation

### Refactor

- remove bytes exchange dispatchers
- remove bytes raw exchange bindings

### Perf

- route raw rest requests through native json
- use native json across exchange wrappers
- use native json in binance wrappers
- add native json response bindings

## 0.26.0 (2026-06-28)

### Feat

- add Gate.io wallet transfer python wrapper

### Fix

- allow clippy argument lint for python bindings
- harden native request error paths

## 0.25.0 (2026-06-28)

### Feat

- replace optional params with builders
- align rust endpoint ergonomics with python

### Fix

- remove unsupported kucoin key version usage

## 0.24.2 (2026-06-22)

### Fix

- repair live websocket connectivity

## 0.24.1 (2026-06-22)

### Perf

- avoid redundant websocket json conversion

## 0.24.0 (2026-06-22)

### Feat

- add aster websocket support
- add backpack websocket support
- add lighter websocket support
- add hyperliquid websocket support

## 0.23.0 (2026-06-21)

### Feat

- add kucoin websocket clients
- add bingx websocket clients
- add gateio websocket clients
- add bitmex websocket clients
- add bitmart websocket clients
- add mexc websocket clients
- add kraken websocket clients
- add bitget private websocket client
- add bybit private websocket client
- add okx private websocket client
- add bitget public websocket client
- add bybit public websocket client
- add binance private websocket client
- add okx public websocket client
- add binance public websocket client

### Fix

- harden websocket private auth state

## 0.22.0 (2026-06-20)

### Feat

- migrate aster to rust core
- migrate backpack to rust core
- migrate lighter to rust core
- migrate hyperliquid to rust core
- migrate kucoin to rust core
- migrate bingx to rust core
- migrate gateio to rust core
- migrate BitMEX to Rust core
- migrate BitMart to Rust core
- move MEXC HTTP APIs to Rust
- move Kraken HTTP APIs to Rust
- move Bitget HTTP APIs to Rust
- move OKX HTTP APIs to Rust
- move Bybit APIs to Rust
- move Binance private APIs to Rust
- move shared product table core to Rust
- migrate exchange HTTP APIs to Rust
- add Rust core for Lighter signing

### Fix

- harden live exchange tests
- add dev tools for clean ci sync
- complete native client cleanup
- handle partial hyperliquid spot closes
- split rust release and stabilize native tests
- align migrated exchange parity paths
- preserve Binance native private errors

### Refactor

- move endpoint routing into rust
- require rust native transport
- move product table rows to rust
- remove python http fallback dependencies
- align rust crate layout and tests
- split large shared modules
- split Python native bindings

## 0.21.2 (2026-06-13)

### Fix

- harden exchange stateful tests

## 0.21.1 (2026-06-13)

### Fix

- implement lighter signing in pure python

## 0.21.0 (2026-06-13)

### Feat

- support bitget uta live tests

### Refactor

- remove lighter sdk signing dependency

## 0.20.3 (2026-06-13)

### Fix

- recreate closed hyperliquid async session

## 0.20.2 (2026-06-13)

### Fix

- preserve async client transport state
- preserve sync client transport state
- calculate decimal places accurately
- validate product table exchange names
- align sync and async endpoint signatures

## 0.20.1 (2026-06-12)

### Fix

- preserve request state and query values
- align exchange request handling
- preserve product fetch failures during cleanup
- preserve lookup and test safety semantics
- harden sanitization and product cleanup
- validate managed fetch context first
- require opt-in for stateful test files
- close remaining request lifecycle gaps
- harden exchange request lifecycle
- address cross-exchange review findings
- harden exchange request handling

### Refactor

- remove unused compatibility parameters

## 0.20.0 (2026-06-11)

### Feat

- add Aster exchange support
- add Backpack exchange support

## 0.19.0 (2026-06-08)

### Feat

- add lighter support

## 0.18.0 (2026-06-07)

### Feat

- add mexc exchange support
- add bitget exchange support

## 0.17.0 (2026-06-06)

### Feat

- add kraken exchange support

## 0.16.0 (2026-06-06)

### Feat

- add hyperliquid live coverage
- expose raw response headers

### Refactor

- remove bitmex parsed rate limit state

## 0.15.0 (2026-06-06)

### Feat

- add binance wallet transfer support

### Fix

- validate okx deposit status queries

## 0.14.0 (2026-06-05)

### Feat

- complete bingx support

## 0.13.0 (2026-06-05)

### Feat

- add kucoin transfer and leverage support
- complete kucoin support
- complete okx endpoint coverage

### Fix

- complete gateio live endpoint coverage
- complete bitmex live endpoint coverage
- complete bitmart live endpoint coverage
- harden bybit v5 live workflows

## 0.12.0 (2026-06-01)

### Feat

- add public market sentiment endpoints

### Refactor

- remove high-risk asset operations

## 0.11.0 (2026-06-01)

### Feat

- expand binance trading coverage

## 0.10.1 (2026-06-01)

### Fix

- wrap gateio json decode errors
- raise on JSON decode failure in all remaining HTTP managers
- harden JSON decode and query-string handling in HTTP managers
- address code review findings across builder fee and test infra

## 0.10.0 (2026-05-31)

### Feat

- **trade**: accept OrderSide in order placement across all exchanges
- **enums**: add unified OrderSide enum
- **base**: emit request/error logs across remaining exchanges
- **base**: emit request/error logs, adopt in binance

### Fix

- harden exchange http managers
- align exchange wrappers with api docs
- align live test gating and hyperliquid builder payload

### Refactor

- **product_table**: share query logic between sync and async
- **base**: drop the unused drop_none helper
- **base**: adopt BaseHTTPManager in bitmex and hyperliquid
- **base**: adopt BaseHTTPManager in bybit, okx, bitmart, gateio
- **base**: add shared HTTP manager base, adopt in binance
- **product_table**: derive fetch lists from a central registry

## 0.9.3 (2026-05-30)

### Fix

- **ci**: enforce ruff gates and fix release bump detection

## 0.9.2 (2025-11-05)

### Fix

- **ptm**: remove unnecessary fields and sync async code to sync version

## 0.9.1 (2025-11-05)

### Fix

- **ci**: update workflow

## 0.9.0 (2025-11-05)

### Feat

- add hyperliquid exchange support
- **zoomex**: initial implementation

## 0.8.0 (2025-11-03)

### Feat

- add kucoin exchange async spot support

## 0.7.0 (2025-11-03)

### Feat

- add bingx exchange async swap support
- add gate exchange support
- add bitmex exchange support

### Fix

- remove trailing whitespace

## 0.6.1 (2025-11-02)

### Fix

- **ci**: update release workflow

## 0.6.0 (2025-11-02)

### Feat

- add bitmart exchange support

## 0.5.0 (2025-11-02)

### Feat

- add bybit exchange support

### Fix

- **ci**: update release workflow

## 0.4.1 (2025-11-01)

### Fix

- **ci**: update release workflow

## 0.4.0 (2025-11-01)

### Feat

- **ascendex**: initial implementation
- add binance exchange support (api, fapi)

## 0.3.4 (2025-10-29)

### Fix

- **ci**: update release workflow

## 0.3.3 (2025-10-29)

### Fix

- **ci**: update release workflow

## 0.3.2 (2025-10-29)

### Fix

- **ci**: update release workflow

## 0.3.1 (2025-10-29)

### Fix

- **ci**: update release workflow

## 0.3.0 (2025-10-28)

### Fix

- **ci**: update release workflow
- **ci**: correct tag prefix in release workflow

## 0.2.1 (2025-10-28)

### Fix

- **ci**: add v prefix to tag_name

## 0.2.0 (2025-10-28)

### Feat

- add okx exchange support
