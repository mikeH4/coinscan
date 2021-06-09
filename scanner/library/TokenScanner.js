const { ethers, providers } = require('ethers');
const { DB } = require('./DB');
const { Token } = require('./Token');
const { Batch } = require('./Batch');
const { Threads, ThreadPool, sleep } = require('./Thread');
const { safeHandler } = require('./errors');
const { LoadManager } = require('./LoadManager');
const { SectionedStack } = require('./SectionedStack');

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
        blockThreading=1,
        providers=[0],
        chunks=4500,
        db=null
    }) {
        if (startFrom === 0) {
            throw new Error("startFrom cannot be 0")
        }
        this.startFrom = startFrom
        this.threading = threading
        this.blockThreading = blockThreading
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

    __prov () {
        // We're not adding this to the thread
        // Should only be used for non heavy/too many requests
        return this.threadPool.__threads[0].provider
    }

    async currentBlock () {} // In Setup

    async setup () {
        this.currentBlock = (new LoadManager(
            this.__prov().getBlockNumber.bind(this.__prov()),
            10000
        )).fetch

        if (this.startFrom === "latest" || this.startFrom < 1) {
            const currentBlock = await this.currentBlock()
            this.startFrom = (
                this.startFrom === "latest" ?
                currentBlock :
                currentBlock+this.startFrom
            )-1;
        }
        else if (this.startFrom >= 1) {}
        else {
            throw new Error("startFrom unknown:",this.startFrom)
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

    async start () {
        const blockThread = new Threads(this.blockThreading,"Block Thread")
        // -1 Since we're starting from here, indicates, we left off before it
        this.processedUntil = this.startFrom-1
        while (true) {
            await blockThread.freed()
            // Also cached, will not fire in most cases
            const current = await this.currentBlock()

            // +1 because we don't to repeat/overlap the ending boundary block
            const from = Math.min(current,this.processedUntil+1)
            // -1 since both from and to are inclusive
            const to = Math.min(current,from+this.chunks-1)
            if (this.processedUntil === to) {
                // sameBlock, useful for new scanning
                // Don't repeat, try again in half a second
                console.log("Try again in half a sec")
                await sleep(500)
                continue
            }
            this.processedUntil = to

            const filters = {
                fromBlock: from,
                toBlock: to,
                topics: [
                    ethers.utils.id("Transfer(address,address,uint256)")
                ]
            }
            const thread = blockThread.checkout(`Chunk ${from}-${to}`)
            this.chunk(filters)
            .catch(error => {
                console.error(error)
                console.log("Error creating chunk")
            })
            .finally(() => thread.release())
        }
        await this.db.close()
    }

    async chunk (filters) {
        const chunkRange = `${filters.fromBlock}-${filters.toBlock}`
        const thread = await this.threadPool.checkout(`getLogs ${chunkRange}`)
        const logs = await safeHandler(
            () => thread.provider.getLogs(filters),{
                log: `Error pullings logs of chunk: ${chunkRange}`
            }
        )
        thread.release()
        if (logs === null) {
            return
        }
        console.log(`Blocks:`,chunkRange)
        console.log("Logs:",logs.length)
        const cachedPairs = await this.getExistingPairs(
            [...new Set(logs.map(log => Token.fAddress(log.address)))]
        )

        const stack = new SectionedStack(300)
        const batch = new Batch(this.commitLiquidityBatch.bind(this),20)
        for (const log of logs) {
            log.blockHash = Token.fAddress(log.blockHash,true)
            log.transactionHash = Token.fAddress(log.transactionHash,true)
            log.address = Token.fAddress(log.address,false)

            const { address, blockHash } = log
            const [parsed,standard] = Token.parseLog(log)
            if (stack.exists(address) || standard !== "erc20") {
                continue
            }
            stack.add(blockHash,address)

            const thread = await this.threadPool.checkout("Liquidity of " + address);
            ((async () => {
                const token = new Token(address,thread.provider)
                if (cachedPairs[token.address]) {
                    await safeHandler(() => token.getPair(cachedPairs[token.address]),{
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
            })()).catch(error => {
                console.error(error)
                console.log("Error in Thread")
            }).finally(() => thread.release())
        }
        await this.threadPool.completed()
        await batch.process()
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