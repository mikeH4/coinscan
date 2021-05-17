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
        lcl = locals()
        for key,_class in CoreToken.__init__.__annotations__.items():
            if key == "return":
                continue
            setattr(self,key,_class(lcl[key]))


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
