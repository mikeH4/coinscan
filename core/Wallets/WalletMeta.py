from core.Token.TokenMeta import TokenMeta
from library.database.postgres import DB
from typing import Optional
from core.types.db_types import ChainEnum, bigint
from library.database.BaseModel import BaseModel
from core.types.AddressHash import AddressHash

class WalletMeta(BaseModel):
    table = "wallet_meta"
    primary = ["id"]

    id: bigint
    is_contract: bool
    bscscan_tag: str

    def __init__(self,
        id: bigint,
        is_contract: bool,
        bscscan_tag: str
    ): pass

    def _upsert_by_id(self, *,
        dont_update: list[str] = [],
        db: Optional[DB] = None,
    ):
        if self.id == 0: raise TypeError("id cannot be 0")
        with self.with_db(db) as db:
            return db.insert(
                self.table,
                self.dict(),
                replace_insert_on=["id"],
                dont_update=dont_update
            )

    def insert_or_update(self,
        *,
        chain: ChainEnum,
        wallet_address: AddressHash,
        dont_update: list[str] = [],
        db: Optional[DB] = None
    ):
        query, values = TokenMeta._prep_query(
            self, # type: ignore
            dont_update=dont_update,
        )

        with self.with_db(db) as db:
            ret = db.get(query,[chain,wallet_address] + values)
            assert ret is not None
            self.id = bigint(ret[0])
        
        return self.id