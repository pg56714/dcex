## 0.14.2 (2026-10-05)

### Fix

- correct private read endpoints found by the live read-only smoke run

## 0.14.1 (2026-10-04)

### Fix

- send keys for Binance market-data routes, sign authenticated KuCoin, OKX and Bybit reads, drop UTA-rejected Bitget classic routes and validate Bitget UTA intervals

## 0.14.0 (2026-10-04)

### BREAKING CHANGE

- resolve market and native symbols from official data and drop Bitget classic APIs rejected for UTA
- make Bitget UTA-only

### Fix

- accept only IOC or POC for BingX spot cancel-replace and treat Kraken FOK precheck as unfilled
- report every exchange error as '{Exchange} API Error: [code] message (HTTP status)'
- reject unsupported order flags and validate amend and batch params

## 0.13.0 (2026-09-30)

### BREAKING CHANGE

- remove legacy aliases and resolve clippy arity warnings

### Fix

- normalize spot stream symbols, log skipped rows and update support docs

### Refactor

- remove obsolete source layout guard tooling

## 0.12.0 (2026-09-30)

### Feat

- support observed public spot streams and clarify trading scope
- expand endpoint coverage and document remaining gaps
- expand endpoint wrappers and regression coverage
- expand trading and risk endpoint coverage

### Fix

- preserve declared array inputs and documented wire formats
- omit blank optional attached order fields
- enforce remaining algo and convenience order decimal bounds
- isolate malformed spot products from perpetual metadata
- validate inputs and fund owners, harden checks and add Ondo spot data
- validate attached orders and enforce fund dispatch ownership
- align numeric wire contracts and fund ownership
- preserve signed peg offsets and canonical alias contracts
- cover leverage fields and verify signed wire inputs
- complete numeric contracts and strengthen audit checks
- restore attached orders and batch decimal contracts
- scope decimal rules to explicit endpoint schemas
- preserve exact coin swap attached prices
- require explicit position sides and repair documentation checks
- enforce order safety and reconcile endpoint coverage
- complete endpoint coverage and reconcile inventory
- address endpoint audit findings and expand regression coverage

### Refactor

- name regression tests and coverage records by behavior
- move Binance subaccount submissions to transfers
- remove redundant Bitget helper borrows
- preserve display inputs for Bitget error helper
- move Lighter submissions into withdrawal owner
- place shared helpers before test modules
- move bridge commitment into withdrawal modules
- consolidate remaining same-prefix error helpers
- remove redundant error message borrows
- consolidate exchange error constructors
- enforce dispatch ownership across exchange modules
- consolidate fund handlers and internal module names
- unify private dispatch and enforce exchange layout
- standardize native test modules and schema adapters
- standardize fund movement and batch modules
- unify schema validation and lossless numeric encoding
- organize exchange modules and schemas by domain

## 0.11.0 (2026-09-25)

### Feat

- add USD-M futures order book wrappers
- add spot wallet read endpoints
- add trading lifecycle and market data endpoints
- add coin futures, convert, and risk-control APIs
- expand advanced exchange trading surfaces
- normalize listed options in product tables
- expand Bybit RFQ, finance, and Launchpool workflows
- add cross-exchange finance and subaccount workflows
- add Binance finance and subaccount workflows
- expand stock, RFQ, and options trading
- add Arcus spot router and expand exchange wrappers
- add Arcus perpetual REST and WebSocket clients
- add perps REST and WebSocket clients

### Fix

- include omitted futures and disambiguate products
- classify stock markets and correct product limits
- complete stock market metadata routing

### Refactor

- modularize Arcus trading workflows

## 0.10.0 (2026-09-14)

### Feat

- support Robinhood network

## 0.9.0 (2026-07-27)

### Feat

- expand tradfi product discovery

## 0.8.0 (2026-07-26)

### Feat

- support tokenized equity trading

### Fix

- align RFQ parameters with official API

## 0.7.1 (2026-07-25)

### Fix

- align Binance and Lighter API validation
- align MEXC and OKX API integrations

## 0.7.0 (2026-07-25)

### BREAKING CHANGE

- remove integration following exchange closure

### Fix

- align exchange APIs with current specifications

## 0.6.5 (2026-07-20)

### Fix

- align exchange order APIs with current specs
- align websocket integrations with exchange specs

## 0.6.4 (2026-07-18)

### Fix

- update KuCoin endpoints and MEXC time sync
- align exchange integrations with official APIs
- align exchange integrations with official APIs
- align exchange websocket integrations
- validate Kraken subscriptions and Extended candles
- align exchange product and websocket contracts

## 0.6.3 (2026-07-13)

### Fix

- align binance and bybit private requests

## 0.6.2 (2026-07-12)

### Fix

- align order requests with exchange contracts
- gate releases and validate Bitget strategy orders

## 0.6.1 (2026-07-12)

### Fix

- enforce Binance account query symbols

## 0.6.0 (2026-07-11)

### Feat

- add plan order and market risk endpoints
- expand advanced exchange endpoints
- add unified trading endpoint wrappers
- split exchange fee rate endpoints

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
