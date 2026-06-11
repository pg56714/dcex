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
