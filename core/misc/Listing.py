from library.postgres import DB
from library.BaseModel import BaseModel
from core.types.Address import Address
from time import time

class Listing(BaseModel):
    table = "listings"
    primary = ["token","platform"]

    def __init__(self, 
        token:Address,
        platform:str,
        local_id:str,
        local_slug:str,
        added:int,
        updated:int,
    ) -> None: pass
    
    @classmethod
    def get_by_platform(cls,platform):
        with DB() as db:
            listings = [cls._from_row(row) for row in db.get_all(
                f"SELECT * FROM listings WHERE platform = %s",
                [platform]
            )]
            return listings

    @classmethod
    def get_addresses_not_inserted(cls,limit=1000,db=None):
        limit_cond = cls.limit_cond(limit)
        with cls.with_db(db) as db:
            addresses = [Address(row[0]) for row in db.get_all(
                f"""
                SELECT listings.token FROM listings
                LEFT JOIN tokens ON tokens.address = listings.token
                WHERE tokens.address IS NULL
                {limit_cond}
                """,
                []
            )]
            return addresses

    @classmethod
    def get_listings(cls, token_address: Address):
        token_address = str(Address(token_address))
        with DB() as db:
            rows = db.get_all(
                f"SELECT * FROM listings WHERE token = {db.placeholder(1)}",
                [token_address]
            )
            return [cls._from_row(row) for row in rows]

    def insert(self,db:DB = None,replace = False,update_added=False):
        data = self.dict()
        data["token"] = str(data["token"])

        with self.with_db(db) as db:
            db.insert(
                self.table,
                data,
                replace_insert_on=self.primary if replace else False,
                commit=False,
                dont_update=[] if update_added else ["added"]
            )