from library.BaseModel import BaseModel
from library.postgres import DB
from core.types.Address import Address
from core.types.db_types import numeric

class Pairs(BaseModel):
    table = "pairs"
    primary = ["token","pair"]

    def __init__(self,
        token: Address,
        pair: Address,
        updated: int
    ) -> None: pass
    
    def insert_or_ignore(
        self,
        db:DB = None
    ):
        data = self.dict()
        data["token"] = str(data["token"])
        data["pair"] = str(data["pair"])

        with self.with_db(db) as db:
            db.insert(
                self.table,
                data,
                ignore_insert=True,
                commit=False
            )
    
    @classmethod
    def count(cls,db:DB = None):
        with cls.with_db(db) as db:
            return int(db.get("SELECT COUNT(*) FROM pairs")[0])

    @classmethod
    def unknown_pairs(cls, db=None, limit=100):
        limit_cond = cls.limit_cond(limit)
        with cls.with_db(db) as db:
            return [
                Address(row[0])
                for row in
                db.get_all(
                    f"""
                    SELECT
                        pairs.pair
                    FROM pairs
                    LEFT JOIN holders ON holders.contract = pairs.pair
                    WHERE holders.contract IS NULL
                    {limit_cond}
                    """
                )
            ]