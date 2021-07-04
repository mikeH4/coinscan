from library.postgres import DB
from time import time
from core.types.Address import Address
from library.BaseModel import BaseModel

class HoldersPulled(BaseModel):
    table = "holders_pulled"
    primary = ["token"]

    def __init__(self, 
        token:Address,
        added:int,
        updated:int
    ) -> None: pass

    def insert_or_update(self,db:DB = None):
        with self.with_db(db) as db:
            _dict = self.dict()
            for attr in ["token"]:
                _dict[attr] = str(_dict[attr])
            
            db.insert(
                self.table,
                _dict,
                replace_insert_on=self.primary,
                dont_update=["added"],
                commit=False
            )

    @classmethod
    def not_updated_recently(cls, db:DB = None, limit=1000):
        with cls.with_db(db) as db:
            print(cls.limit_cond(limit=limit))
            # 24 hours ago
            before = time()-(24*60*60)
            rows = db.get_all(f"""
            SELECT token FROM holders_pulled
            WHERE updated < {before}
            ORDER BY updated ASC
            {cls.limit_cond(limit=limit)}
            """)
            return [row[0] for row in rows]
    
    @classmethod
    def not_updated_at_all(cls, db:DB=None, limit=1000):
        with cls.with_db(db) as db:
            rows = db.get_all(f"""
            SELECT tokens.address FROM tokens
            LEFT JOIN holders_pulled ON holders_pulled.token = tokens.address
            WHERE holders_pulled.token IS NULL
            {cls.limit_cond(limit=limit)}
            """)
            return [row[0] for row in rows]