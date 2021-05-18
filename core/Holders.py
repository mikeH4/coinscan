from library.postgres import DB

from core.Address import Address
from core.BaseModel import BaseModel

class Holders(BaseModel):
    table = "holders"
    primary = ["contract","holder"]

    def __init__(self, 
        contract:Address,
        holder:Address,
        holder_tag:str,
        holding:float,
        updated_time:int,
        source:str,
    ) -> None: pass

    def insert_or_update(self,db:DB = None):
        _db = db if db is not None else DB("tokens")

        _dict = self.dict()
        for attr in ["contract","holder"]:
            _dict[attr] = str(attr)
        _db.insert(
            "tokens",
            _dict,
            replace_insert_on=self.primary,
            commit=False
        )
        print("Inserted holder for ", self.contract )

        if db is None:
            _db.close()