from core.Token.TokenMeta import TokenMeta
from core.types.AddressHash import AddressHash
from library.postgres import DB
from typing import Optional
from library.BaseModel import BaseModel
from core.types.db_types import ChainEnum, bigint, numeric

class WalletHoldings(BaseModel):
    table = "wallet_holdings"
    primary = ["wallet_id","token_id"]

    wallet_id: bigint
    token_id: bigint
    supply: numeric
    liquidity: numeric

    def __init__(self,
        wallet_id: bigint,
        token_id: bigint,
        supply: numeric,
        liquidity: numeric,
    ): pass

    def insert_with_wallet_upsert(self, *,
        chain: ChainEnum,
        wallet_address: AddressHash,
        dont_update: list[str] = [],
        db: Optional[DB] = None
    ):
        with self.with_db(db) as db:
            keys = self.keys
            self.keys.remove("wallet_id")

            update_cmd = []
            values = []
            for key in keys:
                if key in dont_update: continue
                update_cmd.append(f"{key} = excluded.{key}")
                values.append(getattr(self,key))

            query = f"""
            {TokenMeta.address_upsert_sql()}
            INSERT INTO token_meta
            SELECT id,{DB.placeholder(len(keys))} FROM cte
            ON CONFLICT (id)
            DO UPDATE SET {', '.join(update_cmd)}
            RETURNING id
            """
            with self.with_db(db) as db:
                ret = db.get(query,[chain, wallet_address] + values)
                assert ret is not None
                self.id = bigint(ret[0])
            return self.id
    