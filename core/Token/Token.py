from core.Token.TokenMeta import TokenMeta
from library.BaseModel import BaseModel
from library.postgres import DB
from core.sources.BscScanApi import BscScanApi

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
        db=None,
        # Meta
        **kwds
    ):
        kwds["source_verified"] = bscscan_api.source_code(address=address) is not None
        with cls.with_db(db,commit=True) as db:
            Token(
                address=address,
                name=name,
                symbol=symbol
            ).insert_or_update(db=db,ignore=True)
            TokenMeta.update(address,**kwds,db=db)
            print("CommiT")
    
    @classmethod
    def existing_from(cls,of:list=[],db:DB=None):
        with cls.with_db(db) as db:
            if len(of) < 1:
                return []
            of = list(map(str,of))
            placeholder = db.placeholder(len(of))
            sql = f"SELECT address FROM tokens WHERE address IN ({placeholder})"
            addrs = [row[0] for row in db.get_all(sql,of)]
            return addrs
    
    @classmethod
    def permanent_delete(cls,address:Address,db:DB=None):
        with cls.with_db(db) as db:
            sql = f"DELETE FROM tokens WHERE address = {db.placeholder(1)}"
            db.query(sql,[str(address)])