from library.BaseModel import BaseModel
from core.types.Address import Address

class BSCheckRating(BaseModel):
    table = "bscheck_rating"
    primary = ["address"]

    def __init__(self,
        address:Address,
        rating:str,
        honeypot_check:bool,
        owner_renounced:bool,
        dev_liquidity_check:bool,
        lp_check:bool,
        top_holders_check:bool,
        updated:int
    ) -> None: pass