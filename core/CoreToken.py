from datetime import datetime
from core.Address import Address

class CoreToken:
    def __init__(self, 
        name:str,
        symbol:str,
        address:Address,
        block_time:int,
        updated:int,

        # BscScan
        total_supply:int,
        decimals:int,
        source_verified:bool,

        # BscCheck
        rating:str,
        honeypot_check:bool,
        owner_renounced:bool,
        dev_liquidity_check:bool,
        lp_check:bool,
        top_holders_check:bool,

        # TokenSniffer
        deployed:int,
        first_seen:int,
        source_md5:str,
        similar_count:int,
        similar_viewable:int,
        no_older_tokens:bool,
        not_proxy:bool,
        not_pausable:bool,

    ) -> None:
        
        self.name = name
        self.symbol = symbol
        self.address = address
        self.block_time = block_time
        self.updated = updated

        # BscScan
        self.total_supply = total_supply
        self.decimals = decimals
        self.source_verified = source_verified

        # BscCheck
        self.rating = rating
        self.honeypot_check = honeypot_check
        self.owner_renounced = owner_renounced
        self.dev_liquidity_check = dev_liquidity_check
        self.lp_check = lp_check
        self.top_holders_check = top_holders_check


        # TokenSniffer
        self.deployed = deployed
        self.first_seen = first_seen
        self.source_md5 = source_md5
        self.similar_count = similar_count
        self.similar_viewable = similar_viewable
        self.no_older_tokens = no_older_tokens
        self.not_proxy = not_proxy
        self.not_pausable = not_pausable

    keys = [
        "address",
        "name",
        "symbol",
        "block_time",
        "updated",
        "total_supply",
        "decimals",
        "source_verified",
        "rating",
        "honeypot_check",
        "owner_renounced",
        "dev_liquidity_check",
        "lp_check",
        "top_holders_check",
        "deployed",
        "first_seen",
        "source_md5",
        "similar_count",
        "similar_viewable",
        "no_older_tokens",
        "not_proxy",
        "not_pausable"
    ]

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}
