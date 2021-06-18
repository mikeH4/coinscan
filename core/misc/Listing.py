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
    
    _listings_cache = {}
    @classmethod
    def cache_listings(cls,token_addresses):
        notcached = set(token_addresses) - set(cls._listings_cache.keys())
        token_addresses = notcached

        if len(token_addresses) < 1:
            return

        with DB("tokens") as db:
            rows = db.get_all(
                f"SELECT * FROM listings WHERE token IN ({db.placeholder(len(token_addresses))})",
                token_addresses
            )
            for row in rows:
                listing = cls._from_row(row)
                if str(listing.token) not in cls._listings_cache:
                    cls._listings_cache[str(listing.token)] = []
                cls._listings_cache[str(listing.token)].append(listing)
            for notfound in set(token_addresses) - set(cls._listings_cache.keys()):
                cls._listings_cache[notfound] = []

    @classmethod
    def get_by_platform(cls,platform):
        with DB("tokens") as db:
            addresses = [cls._from_row(row) for row in db.get_all(
                f"SELECT * FROM listings WHERE platform = %s",
                [platform]
            )]
            return addresses

    @classmethod
    def new_listings(cls,db:DB = None) -> dict:
        with cls.with_db(db) as db:
            token_listings = {}
            results = db.get_all(
                f"""
                SELECT token,platform,added
                FROM listings
                WHERE added > {time() - 60*60*24}
                ORDER BY added DESC
                """
            )
            for row in results:
                token,platform,added = row
                if token not in token_listings:
                    token_listings[token] = []
                token_listings[token].append(dict(
                    platform=platform,
                    added=added
                ))
            return token_listings

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
        if token_address in cls._listings_cache:
            return cls._listings_cache[token_address]
        with DB("tokens") as db:
            rows = db.get_all(
                f"SELECT * FROM listings WHERE token = {db.placeholder(1)}",
                [token_address]
            )
            return [cls._from_row(row) for row in rows]

    def insert(self,db:DB = None,replace = False,update_added=False):
        data = self.dict()
        data["token"] = str(data["token"])

        _db = DB("tokens") if db is None else db
        _db.insert(
            self.table,
            data,
            replace_insert_on=self.primary if replace else False,
            commit=False,
            dont_update=[] if update_added else ["added"]
        )
        if db is None:
            _db.close()