from typing import Optional
from library.postgres import DB
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, bigint, serial
from library.BaseModel import BaseModel, Index

class Address(BaseModel):
    table = "address"

    primary = ["id"]
    indexes = [Index(cols=["chain","address"],unique=True)]
    
    def __init__(self,
        id: serial,
        chain: ChainEnum,
        address: AddressHash
    ): pass

    @classmethod
    def addresses_from(cls, *, addresses: list[AddressHash], db: DB = None):
        query = f"""
        SELECT * FROM address WHERE address.address IN (
            {DB.placeholder(len(addresses))}
        )
        """
        with cls.with_db(db) as db:
            return [AddressHash(row[0]) for row in db.get_all(query,addresses)]
    
    @staticmethod
    def _confirm_sql():
        return f"""
        INSERT INTO address (chain, address)
        VALUES ({DB.placeholder(2)})
        ON CONFLICT (chain, address) DO UPDATE SET address = address.address
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
