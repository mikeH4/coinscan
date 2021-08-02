from core.Address import Address
from time import time
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
        query, values = TokenMeta._prep_query(self, # type: ignore
            dont_update=dont_update,
            remove_key="wallet_id"
        )

        with self.with_db(db) as db:
            ret = db.get(query,[chain,wallet_address] + values)
            assert ret is not None
            self.id = bigint(ret[0])
        
        return self.id

    @classmethod
    def not_updated(cls, *,
        before_hours: int = 24,
        db: Optional[DB] = None
    ):
        before_time = int(time() - before_hours*60*60)
        with cls.with_db(db) as db:
            query = f"""
            SELECT
                address.id,
                address.chain,
                address.address,
                pair_address.address
            FROM address
            JOIN token_meta ON token_meta.id = address.id
            LEFT JOIN token_pair ON token_pair.token_id = address.id
            LEFT JOIN address AS pair_address ON token_pair.pair_id = pair_address.id
            LEFT JOIN state_time
                ON token_meta.id = state_time.id
                AND state_time.key = 'wallet_supply'
                AND state_time.update IS TRUE
            WHERE state_time.key IS NULL OR (
                state_time.time < {before_time}
            )
            """
            rows = db.get_all(query)

            return [
                (Address._from_row(row),None if row[3] is None else AddressHash(row[3]))
                for row
                in rows
            ]