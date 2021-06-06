from core.misc.Listing import Listing
from library.BaseModel import BaseModel
from library.postgres import DB

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