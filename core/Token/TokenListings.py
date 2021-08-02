from core.Token.TokenMeta import TokenMeta
from library.postgres import DB
from core.types.AddressHash import AddressHash
from library.BaseModel import BaseModel
from core.types.db_types import ChainEnum, PlatformsEnum, bigint

class TokenListings(BaseModel):
    table = "token_listings"
    
    primary = ["id","platform"]

    def __init__(self,
        id: bigint,
        platform: PlatformsEnum,
        local_id: str,
        local_slug: str,
        added: int,
    ): pass

    def insert_or_update(self,
        *,
        chain: ChainEnum,
        token_address: AddressHash,
        dont_update: list[str] = ["added"],
        db: DB = None
    ):
        query, values = TokenMeta._prep_query(
            self, # type: ignore
            dont_update=dont_update,
        )

        with self.with_db(db) as db:
            ret = db.get(query,[chain,token_address] + values)
            assert ret is not None
            self.id = bigint(ret[0])
        
        return self.id