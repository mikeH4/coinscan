from core.types.db_types import numeric
from library.BaseModel import BaseModel
from core.types.Address import Address

class TokenMeta(BaseModel):
    table = "token_meta"
    primary = ["address"]

    null_cols = [
        "decimals",
        "total_supply",
        "source_verified",
        "holders",
        "block_time"
    ]

    def __init__(self,
        address:Address,
        decimals:int = None,
        total_supply:numeric = None,
        source_verified:bool = None,
        holders:int = None,
        block_time:int = None
    ) -> None: pass

    @classmethod
    def update(cls,address:Address,key,value):
        address = Address(address)
        if key not in cls.null_cols:
            raise TypeError("Not a valid key")