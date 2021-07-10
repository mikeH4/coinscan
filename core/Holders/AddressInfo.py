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
    
    def insert(self,db:DB = None):
        data = self.dict()
        data["address"] = str(data["address"])

        with self.with_db(db) as db:
            db.insert(
                self.table,
                data,
                ignore_insert=True,
                commit=False
            )

    @classmethod
    def unknown_holder_contracts(cls,db=None,limit=100):
        limit_cond = cls.limit_cond(limit)
        with cls.with_db(db) as db:
            return [
                row[0]
                for row in
                db.get_all(
                    f"""
                    SELECT
                        DISTINCT holders.contract
                    FROM address_info
                    JOIN holders ON address_info.address = holders.holder
                    WHERE address_info.is_contract IS NULL {limit_cond}
                    """
                )
            ]