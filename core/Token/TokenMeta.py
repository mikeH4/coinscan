from typing import KeysView
from core.types.db_types import numeric
from library.BaseModel import BaseModel
from library.postgres import DB
from core.types.Address import Address, BlockOrTransactionHash

class TokenMeta(BaseModel):
    table = "token_meta"
    primary = ["address"]

    null_cols = [
        "decimals",
        "total_supply",
        "source_verified",
        "holders",
        "liquidity",
        "creation_tx",
        "creator",
        "block_time"
    ]

    def __init__(self,
        address:Address,
        decimals:int = None,
        total_supply:numeric = None,
        source_verified:bool = None,
        holders:int = None,
        liquidity:numeric = None,
        creation_tx:BlockOrTransactionHash = None,
        creator:Address = None,
        block_time:int = None
    ) -> None: pass
    
    @classmethod
    def get(cls,address):
        with DB("tokens") as db:
            return cls._from_row(db.get(
                f"SELECT * FROM token_meta WHERE address = {db.placeholder(1)}",
                [address]
            ))

    @classmethod
    def where_is_none(cls,key,limit=1000):
        limit_cond = cls.limit_cond(limit)
        if key not in cls.keys:
            raise KeyError(f"TokenMeta doesn't have the attribute {key}")
        with DB("tokens") as db:
            return [cls._from_row(row) for row in db.get_all(
                f"""
                SELECT * FROM token_meta
                WHERE {key} IS NULL
                ORDER BY block_time DESC NULLS LAST
                {limit_cond}
                """,
                [key]
            )]

    @classmethod
    def get_addresses(cls,limit=1000,where_cond=""):
        limit_cond = cls.limit_cond(limit)
        with DB("tokens") as db:
            return [row[0] for row in db.get_all(
                f"""
                SELECT tokens.address FROM tokens
                LEFT JOIN token_meta ON tokens.address = token_meta.address
                {where_cond}
                ORDER BY block_time DESC NULLS LAST
                {limit_cond}
                """
            )]

    @classmethod
    def update(
        cls,
        address:Address,
        db = None,
        dont_update=[],
        **kwds
    ):
        with cls.with_db(db) as db:
            cols = kwds.keys()
            col_string = ','.join(cols)
            placeholder = db.placeholder(len(kwds)+1)

            keyed_str = ", ".join([
                f"{key} = excluded.{key}"
                for key in cols
                if key not in dont_update
            ])
            insert_sql = f"INSERT INTO token_meta (address,{col_string}) VALUES ({placeholder})"

            update_sql = f"UPDATE SET {keyed_str}"
            sql = f"""
            {insert_sql}
            ON CONFLICT (address)
            DO {update_sql}
            """
            db.query(sql,[str(Address(address))] + list(kwds.values()))