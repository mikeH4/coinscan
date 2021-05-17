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

    def dict(self):
        return {key:getattr(self,key) for key in self.keys}

CoreToken.keys = list(CoreToken.__init__.__annotations__.keys())
CoreToken.keys.remove("return")