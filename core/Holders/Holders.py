from core.Holders.HoldersPulled import HoldersPulled
from library.timer import timer
from library.postgres import DB
from time import time
from core.types.Address import Address
from library.BaseModel import BaseModel
from core.Token.TokenMeta import TokenMeta

class Holders(BaseModel):
    table = "holders"
    primary = ["contract","holder"]

    def __init__(self, 
        contract:Address,
        holder:Address,
        holding:float
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
        with self.with_db(db) as db:
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
    def update_with_pull(
        cls,
        address: Address,
        bscscan,
        db: DB = None
    ):
        with cls.with_db(db) as db:
            ret = bscscan.holders(address=address)
            
            t = int(time())
            HoldersPulled(token=address,added=t,updated=t).insert_or_update(db=db)
            
            if ret is None:
                return
            
            total,top = ret
            TokenMeta.update(
                address=address,
                db=db,
                holders=total
            )

            Holders.delete_all(contract=address,db=db)
            for holder,address_info in top:
                holder.insert_or_update(db=db)
                if holder.holder != "0x0000000000000000000000000000000000000000":
                    address_info.insert(db=db)