const { ethers } = require('ethers')
const { Client } = require('pg')
const { exit } = require("process");

let client;

const providerUrl = "https://bsc-dataseed2.defibit.io/"
const provider = new ethers.providers.JsonRpcProvider(providerUrl);

const scan = async (startFrom = 0) => {
    const res = await client.query("SELECT address FROM tokens")
    const addresses = res.rows.map(({address}) => address)

    const blockNumber = await provider.getBlockNumber();
    const startAt = Math.max(blockNumber - 500,startFrom);
    const filter = {
        fromBlock: startAt,
        toBlock: blockNumber,
        topics: [
            ethers.utils.id("Transfer(address,address,uint256)")
        ]
    }
    const logs = await provider.getLogs(filter);
    logs.forEach(log => {
        if (!addresses.includes(log.address)) {
            
        }
        DB.addIfNotExists(log.address);
    });
    return blockNumber;
}

(async () => {
    client = new Client({
        host: 'localhost',
        database: 'tokens',
    })
    await client.connect()
    let startFrom = 0;
    while (true) {
        startFrom = await scan(startFrom)
    }
})();
