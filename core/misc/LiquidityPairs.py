from library.BaseModel import BaseModel
from core.types.Address import Address
from core.types.db_types import numeric, smallint

class LiquidityPairs(BaseModel):
    table = "liquidity_pairs"
    primary = ["token"]

    null_cols = ["pancakeswap_pair"]

    def __init__(self,
        token:Address,
        token_decimals:smallint,
        token_reserves:numeric,
        bnb_reserves:numeric,
        is_token0: bool,
        pancakeswap_pair:Address,
        updated:int,
    ) -> None: pass