const { ethers } = require('ethers')
const { Client } = require('pg')

let client;

const providerUrl = "https://bsc-dataseed2.defibit.io/"
const provider = new ethers.providers.JsonRpcProvider(providerUrl);

const sleep = (time = 1000) => new Promise(r => setTimeout(r, time));

class DB {
    static async getall() {
        const hours24Ago = this.now()-(60*60*24);
        const res = await client.query(`SELECT address FROM tokens WHERE updated >= ${hours24Ago}`)
        const requests = await client.query("SELECT address FROM token_requests")
        const addresses = res.rows.concat(requests.rows).map(({ address }) => address)
        return addresses
    }
    static fAddress(address) {
        address = address.toLowerCase()
        if (address.length !== 42) {
            throw new Error(`Address is not of length 42: ${address}`);
        }
        return address;
    }
    static now() {
        return parseInt(Date.now() / 1000);
    }
    static __holding = []
    static async insert({ address }) {
        address = this.fAddress(address);
        this.__holding.push(address);
        if (this.__holding.length < 20) {
            return;
        }
        await this.push();
    }
    static async push() {
        this.__holding = [...new Set(this.__holding)]
        if (this.__holding.length < 1) {
            return;
        }
        await client.query("BEGIN");
        for (const address of this.__holding) {
            const queryText = 'INSERT INTO token_requests(address,request_time) VALUES($1,$2)';
            await client.query(queryText, [address, this.now()]);
        }
        await client.query("COMMIT");
        console.log("Pushed:", this.__holding.length)
        this.__holding = [];
    }
}
const scan = async (startFrom = 0) => {
    const addresses = await DB.getall();
    const blockNumber = await provider.getBlockNumber();
    const startAt = Math.max(blockNumber - 300, startFrom);
    const filter = {
        fromBlock: -300,
        topics: [
            ethers.utils.id("Transfer(address,address,uint256)")
        ]
    }
    const logs = await provider.getLogs(filter);
    for (let { address } of logs) {
        address = DB.fAddress(address)
        if (!addresses.includes(address)) {
            addresses.push(address);
            await DB.insert({ address });
        }
    }
    await DB.push();
    await sleep();
    return blockNumber;
}