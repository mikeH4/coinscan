const { ethers, providers } = require('ethers');
const { LoadManager } = require("./LoadManager");
const { timer } = require('./Thread');

const BNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c";
const DEAD = "0x0000000000000000000000000000000000000000";

class Token {
    static __iface_erc20 = new ethers.utils.Interface([
        "event Transfer(address indexed from, address indexed to, uint value)"
    ]);
    static __iface_erc721 = new ethers.utils.Interface([
        "event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)",
    ]);

    static standardABI = [
        "function name() view returns (string)",
        "function symbol() view returns (string)",
        "function decimals() view returns (uint8)",
        "function totalSupply() external view returns (uint)",
        "function balanceOf(address) view returns (uint)",  
        "function transfer(address to, uint amount)",
        "event Transfer(address indexed from, address indexed to, uint amount)"
    ];

    static fNum = ethers.utils.formatUnits;

    static parseLog (log) {
        try {
            return [Token.__iface_erc20.parseLog(log),"erc20"]
        } catch (error) {
            try {
                return [Token.__iface_erc721.parseLog(log),"erc721"]
            } catch (error) {
                return [null,"other"]
            }
        }
    }

    static fAddress(address,blockHash=false) {
        const hashLength = blockHash ? 66 : 42
        address = address.toLowerCase()
        if (address.length !== hashLength) {
            throw new Error(`Address is not of length 42: ${address}`);
        }
        return address;
    }

    static store = {}
    constructor (token_address, provider) {
        if (Token.store[token_address] instanceof Token) {
            return Token.store[token_address]
        }
        Token.store[token_address] = this;
        this.address = token_address;
        this.provider = provider;
        this.contract = new ethers.Contract(this.address, [
            "event Sync(uint112 reserve0, uint112 reserve1)"
        ], provider );

        this.getDecimals = (new LoadManager(this.getDecimalsActual.bind(this),10**10)).fetch
        this.getInfo = (new LoadManager(this.getInfoActual.bind(this),10**10)).fetch
        this.getTotalSupply = (new LoadManager(this.getTotalSupplyActual.bind(this),1000*60*10)).fetch
        this.getLiquidity = (new LoadManager(this.getLiquidityActual.bind(this),1000*60*1)).fetch
    }

    // Added by constructor
    async getDecimals () {}
    async getTotalSupply () {}
    async getInfo () {}
    async getLiquidity () {}

    async getTotalSupplyActual() {
        let totalSupply = null
        try {
            totalSupply = await this.contract.totalSupply()
            return Token.fNum(totalSupply,0);
        } catch (error) {
            console.log("Error getting totalSupply:",totalSupply)
            return 0
        }
    }

    async getDecimalsActual () {
        return await this.getProp("decimals",-1)
    }

    async getInfoActual () {
        const decimals = this.getDecimals()
        return {
            address: this.address,
            name: await this.getProp("name",""),
            symbol: await this.getProp("symbol",""),
            decimals,
            total_supply: await this.getTotalSupply(),
            standard: decimals === -1 ? "other" : "erc20"
        }
    }

    async getProp(prop,fallback) {
        try {
            return await this.contract[prop]()
        } catch (error) {
            console.log("Error with prop (exactly)",prop,":",this.address)
            return fallback
        }
    }

    // Price Factory
    static PancakeFactory = null

    __pairCached
    __pairCachedTime = 0

    async getPair (
        {
            pairAddress,
            tokenPosition
        } = {
            pairAddress:null,
            tokenPosition:null
        }
    ) {
        if (typeof this.__pairCached !== "undefined") {
            if (this.__pairCached !== null) {
                return this.__pairCached
            }
            if ( (Date.now() - this.__pairCachedTime) < 1000*60*3) {
                return null 
                // Or just return this.__pairCached, which is null
            }
        }
        const { provider } = this
        if (Token.PancakeFactory === null) {
            Token.PancakeFactory = new ethers.Contract(
                "0xca143ce32fe78f1f7019d7d551a6402fc5350c73", [
                "function getPair(address tokenA, address tokenB) view returns (address pair)",
            ], provider);
        }

        const pancakePairAddress = (
            pairAddress === null ?
            await Token.PancakeFactory.getPair(this.address,BNB) :
            pairAddress
        ).toLowerCase()
        if (pancakePairAddress === DEAD) {
            this.__pairCached = null
            this.__pairCachedTime = Date.now()
            return null
        }
        const pair = (new ethers.Contract(
            pancakePairAddress,[
                "function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)",
                "function token0() external view returns (address)",
            ], provider
        ));
        pair.tokenPosition = (
            tokenPosition === null ?
            ((await pair.token0()) === BNB ? 1 : 0) :
            tokenPosition
        )
        this.__pairCached = pair
        this.__pairCachedTime = Date.now()
        return pair
    }

    async getLiquidityActual () {
        const pair = await this.getPair()
        if (pair === null) {
            return null
        }
        const decimals = await this.getDecimals()
        if (decimals === -1) {
            return null
        }
        const { tokenPosition } = pair
        const reserves = await pair.getReserves();
        const token_reserves = parseFloat(Token.fNum(reserves[tokenPosition],decimals));
        const bnb_reserves = parseFloat(Token.fNum(reserves[tokenPosition ? 0 : 1],18));                

        return {
            token: this.address,
            token_decimals: decimals,
            token_reserves,
            bnb_reserves,
            is_token0: tokenPosition === 0,
            pancakeswap_pair: pair.address,
            updated: parseInt(Date.now()/1000),
        }
    }
}

exports.Token = Token