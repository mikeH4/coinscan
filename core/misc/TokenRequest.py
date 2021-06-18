from library.BaseModel import BaseModel
from core.types.Address import Address
from library.postgres import DB

class TokenRequest(BaseModel):
    table = "token_requests"
    primary = ["address"]

    def __init__(self, 
        address:Address,
        request_time:int,
    ) -> None: pass

    def insert_or_ignore(self,db:DB = None):
        _db = db if db is not None else DB("tokens")

        _dict = self.dict()
        for attr in ["address"]:
            _dict[attr] = str(_dict[attr])
        
        _db.insert(
            self.table,
            _dict,
            replace_insert_on=self.primary,
            ignore_insert=True,
            commit=False
        )
        print("Inserted/Ignored token request for ", self.address )

        if db is None:
            _db.close()
    
    def remove(self, db: DB = None):
        with self.with_db(db) as db:
            db.query("DELETE FROM token_requests WHERE address = %s",[str(self.address)])

    @staticmethod
    def _get_ordered_in_rows(limit=1000):
        limit_cond = TokenRequest.limit_cond(limit)

        with DB("tokens") as db:
            return db.get_all(f"SELECT * FROM token_requests ORDER BY request_time ASC {limit_cond}")

    @classmethod
    def get_ordered(cls, limit=1000):
        rows = cls._get_ordered_in_rows(limit=limit)
        return [cls._from_row(row) for row in rows]