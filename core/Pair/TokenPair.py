from core.types.AddressHash import AddressHash
from library.postgres import DB
from typing import Optional
from library.BaseModel import BaseModel
from core.types.db_types import ChainEnum, bigint

class TokenPair(BaseModel):
    primary = ["token_id","pair_id"]

    table = "token_pair"

    def __init__(self,
        token_id: bigint,
        pair_id: bigint
    ): pass

    @classmethod
    def count(cls, *,
        chain: Optional[ChainEnum] = None,
        db: Optional[DB] = None,
    ):
        with cls.with_db(db) as db:
            cond = "" if chain is None else f"""
            JOIN address ON address.id = token_pair.token_id
            WHERE address.chain = {db.placeholder(1)}
            """
            params = [] if chain is None else [chain]
            with cls.with_db(db) as db:
                row = db.get(f"""
                SELECT COUNT(*) FROM token_pair
                {cond}
                """, params)
                assert row is not None
                return int(row[0])

    @classmethod
    def insert_or_ignore(cls, *,
        chain: ChainEnum,
        token_address: AddressHash,
        pair_address: AddressHash,
        db: Optional[DB] = None
    ):
        with cls.with_db(db) as db:
            sql = f"""
            WITH cte AS (
                INSERT INTO address (chain, address)
                VALUES
                    ({db.placeholder(2)}),
                    ({db.placeholder(2)})
                ON CONFLICT (chain, address)
                DO UPDATE SET address = excluded.address
                RETURNING id, address
            )
            INSERT INTO token_pair
            SELECT
                (SELECT cte.id FROM cte WHERE cte.address = {db.placeholder(1)}),
                (SELECT cte.id FROM cte WHERE cte.address = {db.placeholder(1)})
            FROM cte
            ON CONFLICT DO NOTHING
            """
            db.query(sql,[
                chain, token_address,
                chain, pair_address,
                token_address, pair_address
            ])