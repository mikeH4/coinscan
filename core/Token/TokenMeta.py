import inspect
from core.Address import Address
from typing import Optional
from library.postgres import DB
from core.types.AddressHash import AddressHash
from library.BaseModel import BaseModel, ModelOperator
from core.types.db_types import ChainEnum, bigint

class TokenMeta(BaseModel):
    table = "token_meta"
    primary = ["id"]

    id: bigint
    name: str
    symbol: str
    decimals: int
    created_time: int
    source_verified: bool

    def __init__(self,
        *,
        id: bigint,
        name: str,
        symbol: str,
        decimals: int,
        created_time: int,
        source_verified: bool = None
    ): pass

    @staticmethod
    def address_upsert_sql():
        return f"""WITH cte AS ( {Address._confirm_sql()} )"""

    def _prep_query(self, *,
        dont_update: list[str] = [],
        remove_key: str = "id"
    ):
        keys = self.keys.copy()
        keys.remove(remove_key)

        update_cmd = []
        values = []
        for key in keys:
            values.append(getattr(self,key))
            if key in dont_update: continue
            update_cmd.append(f"{key} = excluded.{key}")

        query = f"""
        {TokenMeta.address_upsert_sql()}
        INSERT INTO {self.table}
        SELECT id,{DB.placeholder(len(keys))} FROM cte
        ON CONFLICT ({', '.join(self.primary)})
        DO UPDATE SET {', '.join(update_cmd)}
        RETURNING {remove_key}
        """

        return query, values

    def insert_or_update(self,
        *,
        chain: ChainEnum,
        token_address: AddressHash,
        dont_update: list[str] = ["created_time"],
        db: DB = None
    ):
        query, values = TokenMeta._prep_query(self, dont_update=dont_update) #type: ignore

        with self.with_db(db) as db:
            ret = db.get(query,[chain,token_address] + values)
            assert ret is not None
            self.id = bigint(ret[0])
        
        return self.id
    
    @classmethod
    def update(cls, *,
        chain: ChainEnum,
        token_address: AddressHash,
        db: DB = None,
        **kwds
    ):
        parameters = inspect.signature(cls.__init__).parameters
        full_kwds = {}
        dont_update = []
        for key in cls.keys:
            if key in kwds:
                full_kwds[key] = kwds[key]
            else:
                _class = parameters[key].annotation
                full_kwds[key] = ModelOperator.py_defaults[_class]
                dont_update.append(key)
        TokenMeta(**full_kwds).insert_or_update(
            chain=chain,
            token_address=token_address,
            dont_update=dont_update,
            db=db
        )
    
    @classmethod
    def get_addresses(cls, *,
        where_cond: str = "",
        limit: Optional[int] = None,
        db: Optional[DB] = None
    ):
        cls.limit_cond(limit)
        with cls.with_db(db) as db:
            rows = db.get_all(f"""
            SELECT
                address.address
            FROM token_meta
            JOIN address ON address.id = token_meta.id
            {where_cond}
            """)
            return [AddressHash(row[0]) for row in rows]
