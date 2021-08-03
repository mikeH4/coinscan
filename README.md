# Coin Scan

At the core, the database consists of a single table:

```
AddressInfo:
    id: serial
    chain: ChainEnum
    address:    
```

Each Address can be a wallet, token, pair or all 3. Each address can have associated meta for all types:

## 1. `token`

#### `TokenMeta`
For generally static meta about the token
```
TokenMeta:
    id: bigint
    name: str
    symbol: str
    decimals: int
    created_time: int
    source_verified: bool
```

#### `TokenStats`
For dynamic, regularly updating data related to the token
```
TokenStats:
    id: bigint
    total_supply: numeric
    circulating: numeric
    price_change: bigint
    holders: numeric
    liquidity: numeric
```

#### `TokenListings`
For listings from places like CoinGecko and CoinMarketCap
```
TokenListings:
    id: bigint
    platform: PlatformsEnum
    local_id: str
    local_slug: str
    added: int
```

## 2. `wallet`

#### `WalletMeta`
For meta related to the wallet:
```
WalletMeta:
    id: bigint
    is_contract: bool
    bscscan_tag: str
```

#### `WalletHoldings`
For holdings, and liquidity of a particular token:
```
WalletHoldings:
    token_id: bigint
    holder_id: bigint
    supply: numeric
    liquidity: numeric
```

## 3. `pair`
Pair lookup for each token:
#### `TokenPair`
```
TokenPair:
    pair_id: bigint
    token_id: bigint
```

## Additional
#### `StateTime`
Keeps track of added/updated time for particular objects
```
StateTime:
    key: str
    id: bigint
    time: int
    update: bool
```