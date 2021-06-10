const { ethers, providers } = require('ethers');
const { DB } = require('./DB');
const { Token } = require('./Token');
const { Batch } = require('./Batch');
const { Threads, ThreadPool, sleep } = require('./Thread');
const { safeHandler } = require('./errors');
const { KeyedDelayedBatcher } = require('./DelayedBatcher');

const PROVIDER_URLS = [
    // Main
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc-dataseed1.ninicoin.io/",
    // Backup
    "https://bsc-dataseed2.defibit.io/",
    "https://bsc-dataseed3.defibit.io/",
    "https://bsc-dataseed4.defibit.io/",
    "https://bsc-dataseed2.ninicoin.io/",
    "https://bsc-dataseed3.ninicoin.io/",
    "https://bsc-dataseed4.ninicoin.io/",
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/"
];

class TokenScanner {
    db = null;
    processedUntil = null;
    
    constructor ({
        startFrom=1,
        threading=6,
        providers=[0],
        chunks=4500,
        db=null
    }) {
        // This new class concept defines -1 differently,
        // like a normal array/list, where -1 is the last item,
        // -2, the second last, and so on, instead of currentBlock-1
        // "latest" does not exist, since it has been replaced by -1
        if (startFrom === 0) {
            throw new Error("startFrom cannot be 0")
        }
        this.startFrom = startFrom
        this.threading = threading
        this.chunks = chunks
        // Database DB
        this.db = db instanceof DB ? db : new DB("tokens")

        // Thread Pool
        const threads = []
        for (const providerIndex of providers) {
            const thread = new Threads(this.threading)
            thread.provider = new ethers.providers.JsonRpcProvider(
                PROVIDER_URLS[providerIndex]
            )
            threads.push(thread)
        }
        this.threadPool = new ThreadPool(threads)
    }

    async setup () {
        if (this.startFrom < 1) {
            const thread = await this.threadPool.checkout(`currentBlock`)
            const currentBlock = await thread.provider.getBlockNumber()
            thread.release()
            const fromEnd = (this.startFrom*-1)-1
            this.startFrom = currentBlock-fromEnd
        }
        return this
    }

    async commitLiquidityBatch (items) {
        await this.db.commitBlock(client => {
            for (const liquidity of items) {
                client.insert(
                    "liquidity_pairs",
                    liquidity,
                    {commit: false, replace_on: ["token"]}
                )
            }
            console.log(`Commited ${items.length} token's liquidity`)
        })
    }

    async pull () {
        // Initialize stack that is used to let go of existing tokens
        this.batcher = new KeyedDelayedBatcher()

        // -1 Since we're starting from here, indicates, we left off before it
        this.processedUntil = this.startFrom-1
        while (true) {
            const from = this.processedUntil+1
            // -1 Since filters are inclusive
            const to = from+this.chunks-1
            this.processedUntil = to

            const filters = {
                fromBlock: from,
                toBlock: to,
                topics: [
                    ethers.utils.id("Transfer(address,address,uint256)")
                ]
            }
            const thread = await this.threadPool.checkout(`getLogs ${from}-${to}`)
            const logs = await safeHandler(
                () => thread.provider.getLogs(filters),{
                    log: `Error pullings logs of chunk: ${chunkRange}`
                }
            )
            for (const log of logs) {
                log.address = Token.fAddress(log.address,false)
    
                const [parsed,standard] = Token.parseLog(log)
                if (standard !== "erc20") {
                    continue
                }

                this.batcher.update(log.address,log.address)
            }
            thread.release()
        }
        await this.db.close()
    }

    async process () {
        let i = 0
        while (true) {
            i++;
            const addresses = this.batcher.collect()
            // Addresses are already unique inside a keyed batcher
            const existingPairs = await this.getExistingPairs(
                addresses
            )

            const batch = new Batch(this.commitLiquidityBatch.bind(this),20)

            for (const address of addresses) {
                const thread = await this.threadPool.checkout(`Processing batch ${i}`);
                (async () => {
                    try {
                        const token = new Token(address,thread.provider)
                        if (existingPairs[token.address]) {
                            await safeHandler(() => token.getPair(existingPairs[token.address]),{
                                log: "Error getting Pair",
                            })
                        }
                        const liquidity = await safeHandler(() => token.getLiquidity(address),{
                            log: "Error getting liquidity",
                        })
                        if (liquidity === null) {
                            return
                        }
                        await batch.add(liquidity)
    
                    } catch (error) {
                        console.error("Error with token")
                    }
                })()
                .catch(console.error)
                .finally(() => {
                    thread.release()
                })    
            }
        }
    }

    async getExistingPairs (from) {
        const rows = await this.db.getall(
            `SELECT * FROM liquidity_pairs WHERE token IN (${this.db.placeholder(from.length)})`,
            from
        )
        const map = {}
        for (const row of rows) {
            map[row.token] = {
                pairAddress: row.pancakeswap_pair,
                tokenPosition: row.is_token0 ? 0 : 1
            }
        }
        return map
    }
}
exports.TokenScanner = TokenScanner