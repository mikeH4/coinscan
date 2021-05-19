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
            _dict[attr] = str(_dict[attr])
        _db.insert(
            self.table,
            _dict,
            replace_insert_on=self.primary,
            commit=False
        )
        print("Inserted holder for ", self.contract, ":",self.holder )

        if db is None:
            _db.close()
    
    _holders_cache = {}

    @classmethod
    def _prep_holders(cls, addresses, limit=5):
        if len(addresses) < 1:
            return []
        with DB("tokens") as db:
            plc = db.placeholder(len(addresses))
            holders_result = db.get_all(f"""
            SELECT *
            FROM holders holders_outer
            JOIN LATERAL (
                SELECT * FROM holders holders_inner
                WHERE holders_inner.contract = holders_outer.contract
                ORDER BY holders_inner.holding DESC
                LIMIT {db.placeholder(1)}
            ) holders_top ON True
            WHERE holders_outer.contract IN ({plc})
            ORDER BY holders_outer.contract;
            """,[str(limit)] + addresses)

            grouped = {}
            for row in holders_result:
                holder = cls._from_row(row)
                contract = str(holder.contract)
                if contract not in grouped:
                    grouped[contract] = []
                grouped[contract].append(holder)
            
            for non_existing_addr in set(addresses) - set(grouped.keys()):
                grouped[non_existing_addr] = []
            
            cls._holders_cache[limit] = grouped

            return grouped

    @classmethod
    def get_by_address(cls, address, limit = 5):
        if limit in cls._holders_cache and address in cls._holders_cache[limit]:
            return cls._holders_cache[limit][address]
        limit_cond = cls.limit_cond(limit)
        with DB("tokens") as db:
            placeholder = db.placeholder(1)
            rows = db.get_all(f"SELECT * FROM holders WHERE contract = {placeholder} ORDER BY holding DESC {limit_cond}",[str(address)])
            return [cls._from_row(row) for row in rows]