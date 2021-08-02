from library.BaseModel import BaseModel
from core.types.db_types import bigint

class TokenPair(BaseModel):
    primary = ["token_id","pair_id"]

    table = "token_pair"

    def __init__(self,
        token_id: bigint,
        pair_id: bigint
    ): pass