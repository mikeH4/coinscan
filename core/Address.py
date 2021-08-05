from typing import Optional
from library.database.postgres import DB
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, bigint, serial
from library.database.BaseModel import BaseModel, Index

class Address(BaseModel):
    table = "address"

    primary = ["id"]
    indexes = [Index(cols=["chain","address"],unique=True)]

    id: serial
    chain: ChainEnum
    address: AddressHash

    def __init__(self,
        id: serial,
        chain: ChainEnum,
        address: AddressHash
    ): pass

    @classmethod
    def addresses_from(cls, *,
        chain: ChainEnum,
        addresses: list[AddressHash],
        limit: Optional[int] = None,
        db: Optional[DB] = None
    ):
        objs = cls.filter(
            where_cond=f"WHERE address IN ({DB.placeholder(len(addresses))}) AND chain = '{chain}'",
            params=addresses,
            limit=limit,
            db=db
        )
        return [obj.address for obj in objs]
    
    @classmethod
    def filter(cls, *,
        where_cond: str = "",
        limit: Optional[int] = None,
        params: list = [],
        db: Optional[DB] = None
    ):
        with cls.with_db(db) as db:
            rows = db.get_all(f"""
            SELECT
                address.id,
                address.chain,
                address.address
            FROM address
            {where_cond}
            {cls.limit_cond(limit)}
            """,params)
            return [cls._from_row(row) for row in rows]

    @staticmethod
    def _confirm_sql():
        return f"""
        INSERT INTO address (chain, address)
        VALUES ({DB.placeholder(2)})
        ON CONFLICT (chain, address)
        DO UPDATE SET address = address.address
        RETURNING id
        """

    @classmethod
    def _confirm(cls, *,
            chain: ChainEnum,
            address: AddressHash,
            db: Optional[DB] = None
        ):
        with cls.with_db(db) as db:
            res = db.get(cls._confirm_sql(),[chain,address])
            assert res is not None
            return bigint(res[0])
