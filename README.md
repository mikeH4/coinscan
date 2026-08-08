# coinscan

dex analytics for eth + bsc. built it solo in 2021, i was 18. it ran live at coinscan.finance with a reddit bot people actually summoned.

it watched every new trading pair the second it hit pancakeswap / uniswap / sushi, priced it per block, tracked who was holding and who was dumping, and checked whether a token was a honeypot before you aped in. ~1200 commits over 6 months, three languages, no LLM because there wasn't one.

fastest dex scanner in the world at the time, and not by accident: everything else did a database read on every request. i kept the entire token/pair/wallet graph in RAM and hot-swapped it, so a page load was a map lookup, not a query. dextools and poocoin spun. this didn't.

this repo maps the 9 sub-codebases and microservices it's built from:

- ![ts](https://img.shields.io/badge/TS-3178C6?logo=typescript&logoColor=white&style=flat-square) [coinscan-indexer](https://github.com/mikeH4/coinscan-indexer) — the on-chain engine, 11 scanners. start here.
- ![go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white&style=flat-square) [api-balancer](https://github.com/mikeH4/api-balancer) — whole graph in memory, gob hot-swap, zero-downtime
- ![ts](https://img.shields.io/badge/TS-3178C6?logo=typescript&logoColor=white&style=flat-square) [coinscan-frontend](https://github.com/mikeH4/coinscan-frontend) — react, every chart hand-drawn in d3, no lib
- ![py](https://img.shields.io/badge/Py-3776AB?logo=python&logoColor=white&style=flat-square) [coinscan-offchain](https://github.com/mikeH4/coinscan-offchain) — holders, listings, source verification
- ![ts](https://img.shields.io/badge/TS-3178C6?logo=typescript&logoColor=white&style=flat-square) [coinscan-cacher](https://github.com/mikeH4/coinscan-cacher) — ttl merge layer in front of the apis
- ![ts](https://img.shields.io/badge/TS-3178C6?logo=typescript&logoColor=white&style=flat-square) [coinscan-reddit-bot](https://github.com/mikeH4/coinscan-reddit-bot) — summon it, it reads the token off the comment chain, posts price/mcap/liq/holders/scam flags
- ![go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white&style=flat-square) [balancer](https://github.com/mikeH4/balancer) — rate-limit-aware request gateway, per-host quotas, proxy rotation
- ![go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white&style=flat-square) [go-http-proxy](https://github.com/mikeH4/go-http-proxy) — the proxy fleet node
- ![py](https://img.shields.io/badge/Py-3776AB?logo=python&logoColor=white&style=flat-square) [this repo](https://github.com/mikeH4/coinscan) — v1 python core + custom orm, and the map you're reading

## what it all did

- watched every new pair. bsc/pancake + eth uni-v2/v3 + sushi.
- priced per block. uni v3 is concentrated liquidity, so a naive price read is one rpc call per pool per block and you die. instead: one multicall per block that reads sqrtPrice + liquidity for every pool at once.
- tracked holders, dev wallets, ownership transfers. if the deployer moved out or renounced, you saw it.
- **sell check**: replayed transfers to see if wallets that weren't the dev could actually sell. if only the dev can sell, it's a honeypot. flagged red in the ui before the chart even loads.
- served the whole token / pair / wallet graph out of RAM so nothing was a db round-trip.

## the shape of it

```
eth+bsc nodes
     │
     ▼
 indexer (ts, ethers)  ── 11 scanners: blocks, pairs, reserves, v3 pools,
     │                    transfers, holders, owners, burns, supply, sell-check
     ▼
  postgres  ◄──  offchain (py): holders, cex listings, source-verify
     │
     ▼
 api-balancer (go)  ── entire graph lives in a map in memory. rebuild from
     │                 postgres into a gob snapshot, hot-swap it in with zero
     │                 downtime. every sort/filter/net-worth query is in-ram.
     ▼
 nuster cache (1.5gb)  →  cacher (ttl merge)  →  frontend (react)
     │                                             charts drawn by hand in d3.
     ▼                                             no chart library.
 reddit bot (u/coinscan-bot)
```

all outbound rpc/scrape traffic went through my own gateway, because the free
tier limits are brutal: bsc-dataseed is 10k calls / 300s, bscscan is 1 call / 2s.
you build the throttle + a proxy pool or you get banned in an afternoon.

## numbers

- ~1200 commits, 6 months, solo
- eth + bsc, both, per block
- 3 languages by necessity, not for fun
- 1.5gb edge cache, 120-connection postgres pools
- 2021. i was 18. none of it is generated.
