## 0.5.0 (2026-07-10)

### Feat

- add Extended WebSocket streams
- add Extended exchange support

### Fix

- align Extended order signing with API
- stabilize core benchmark measurements

## 0.4.4 (2026-07-02)

### Fix

- harden live private cleanup and throttling
- harden live stateful cleanup

## 0.4.3 (2026-06-29)

### Fix

- require API key for listen key requests
- require BitMEX credentials for signed requests

## 0.4.2 (2026-06-29)

### Fix

- satisfy product table lint checks
- align native params and timeout validation

### Perf

- reduce product table lookup allocations

## 0.4.1 (2026-06-28)

### Fix

- harden native request error paths
- expose Gate.io transfer request helpers

## 0.4.0 (2026-06-28)

### Feat

- replace optional params with builders
- align rust endpoint ergonomics with python

### Fix

- refine builder params and lint checks

## 0.3.2 (2026-06-22)

### Fix

- repair live websocket connectivity

## 0.3.1 (2026-06-22)

### Perf

- avoid redundant websocket json conversion

## 0.3.0 (2026-06-22)

### Feat

- add aster websocket support
- add backpack websocket support
- add lighter websocket support
- add hyperliquid websocket support

### Fix

- preserve hyperliquid websocket coin symbols

## 0.2.0 (2026-06-21)

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

## 0.1.0 (2026-06-20)

### Feat

- expose hyperliquid and lighter rust APIs
- migrate aster to rust core
- migrate backpack to rust core
- migrate lighter to rust core
- migrate hyperliquid to rust core
- migrate kucoin to rust core
- migrate bingx to rust core
- migrate gateio to rust core
- move shared product table core to Rust
- migrate exchange HTTP APIs to Rust
- add Rust core for Lighter signing

### Fix

- harden live exchange tests
- complete native client cleanup
- split rust release and stabilize native tests
- complete kucoin live migration

### Refactor

- move endpoint routing into rust
- remove python http fallback dependencies
- align rust crate layout and tests
