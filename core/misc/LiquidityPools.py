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

        with self.with_db(db) as db:
            db.insert(
                self.table,
                data,
                ignore=True,
                commit=False
            )