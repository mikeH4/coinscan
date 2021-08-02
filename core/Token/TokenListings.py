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
        keys = self.keys
        self.keys.remove("id")

        update_cmd = []
        values = []
        for key in keys:
            if key in dont_update: continue
            update_cmd.append(f"{key} = excluded.{key}")
            values.append(getattr(self,key))

        query = f"""
        {TokenMeta.address_upsert_sql()}
        INSERT INTO token_listings
        SELECT id,{DB.placeholder(len(keys))} FROM cte
        ON CONFLICT (id)
        DO UPDATE SET {', '.join(update_cmd)}
        RETURNING id
        """
        with self.with_db(db) as db:
            self.id = db.get(query,[chain, token_address] + values)[0]
        return bigint(self.id)
    