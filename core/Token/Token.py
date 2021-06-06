from core.Token.TokenMeta import TokenMeta
from re import S
from library.BaseModel import BaseModel
from library.postgres import DB
from core.sources.BscScanApi import BscScanApi

from core.types.db_types import numeric
from core.types.Address import Address

class Token(BaseModel):
    table = "tokens"
    primary = ["address"]

    def __init__(self,
        address:Address,
        name:str,
        symbol:str,
    ) -> None: pass
    
    def insert_or_update(self,
        db:DB = None,
        dont_update:list=[],
        ignore=False
    ):
        with self.with_db(db) as db:
            dict = self.dict()
            dict["address"] = str(dict["address"])
            db.insert(
                "tokens",
                dict,
                replace_insert_on=["address"],
                commit=False,
                dont_update=dont_update,
                ignore_insert=ignore
            )
            print("Inserted:", self.address)
    
    @classmethod
    def insert_with_source(cls,
        bscscan_api:BscScanApi,
        # Required
        address:Address,
        name:str,
        symbol:str,
        # Meta
        **kwds
    ):
        kwds["source_verified"] = bscscan_api.source_code(address=address) is not None
        with DB("tokens") as db:
            Token(
                address=address,
                name=name,
                symbol=symbol
            ).insert_or_update(db=db,ignore=True)
            TokenMeta.update(address,**kwds,db=db)