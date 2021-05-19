from core.BaseModel import BaseModel
from core.Address import Address


class CoreToken(BaseModel):
    table = "tokens"
    primary = ["address"]

    def __init__(self, 
        address:Address,
        name:str,
        symbol:str,
        block_time:int,
        description:str,
        bscscan_img:str,
        holders:int,
        updated:int,

        # BscScan
        total_supply:float,
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

    ) -> None: pass
