from library.postgres import DB

from time import time
from core.types.Address import Address
from library.BaseModel import BaseModel

class Holders(BaseModel):
    table = "holders"
    primary = ["contract","holder"]

    def __init__(self, 
        contract:Address,
        holder:Address,
        holding:float,
        updated_time:int,
        source:str,
    ) -> None: pass

    @staticmethod
    def delete_all(contract: Address,db:DB = None):
        with Holders.with_db(db) as db:
            contract = str(Address(contract))
            
            db.query(
                f"DELETE FROM holders WHERE contract = {db.placeholder(1)}",
                [str(contract)]
            )

    def insert_or_update(self,db:DB = None):
        with Holders.with_db(db) as db:
            _dict = self.dict()
            for attr in ["contract","holder"]:
                _dict[attr] = str(_dict[attr])
            
            db.insert(
                self.table,
                _dict,
                replace_insert_on=self.primary,
                commit=False
            )
            print(f"Inserted holder for {self.contract}: {self.holder}")
    
    @classmethod
    def top(cls, address: Address, limit=10):
        address = str(Address(address))
        limit_cond = cls.limit_cond(limit)
        with DB("tokens") as db:
            query = f"SELECT * FROM holders WHERE contract = {db.placeholder(1)} ORDER BY holding DESC {limit_cond}"
            tokens = db.get_all(query,[address])
            return [cls._from_row(token) for token in tokens]
    
    @classmethod
    def not_updated_recently(cls,db:DB = None):
        with cls.with_db(db) as db:
            hours12_ago = time() - (60*60*12)
            return [row[0] for row in db.get_all(f"""
            SELECT
                DISTINCT contract,
                updated_time
            FROM holders
            WHERE updated_time < {hours12_ago}
            ORDER BY updated_time ASC
            LIMIT 1000
            """)]