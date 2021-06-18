from library.BaseModel import BaseModel
from core.types.Address import Address
from library.postgres import DB

class AddressInfo(BaseModel):
    table = "address_info"
    primary = ["address"]

    null_cols = ["is_contract"]

    def __init__(self,
        address:Address,
        is_contract:bool,
        bscscan_tag:str,
        updated:int,
        added:int
    ) -> None: pass
    
    def insert(self,db:DB = None,replace = False):
        data = self.dict()
        data["address"] = str(data["address"])

        with self.with_db(db) as db:
            db.insert(
                self.table,
                data,
                replace_insert_on=self.primary if replace else False,
                commit=False,
                dont_update=["added"]
            )
    
    @classmethod
    def unknown_contract(cls,db=None,limit=100):
        limit_cond = cls.limit_cond(limit)
        with cls.with_db(db) as db:
            return [
                cls._from_row(row)
                for row in
                db.get_all(f"SELECT * FROM address_info WHERE is_contract IS NULL {limit_cond}")
            ]