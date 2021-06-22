from library.BaseViewableModel import BaseViewableModel
from library.postgres import DB
from library.BaseModel import BaseModel
from core.types.Address import Address
from time import time

class ViewableListings(BaseModel):
    def __init__(self, 
        token:str,
        platform:str,
        added:int,
        local_slug:str,
    ) -> None:
        self.platform = str(platform)
        self.added = int(added)
        self.link = self.listing_link(platform,local_slug)
        if hasattr(self,"local_slug"):
            del self.local_slug

    @classmethod
    def listing_link(cls,platform,local_slug):
        if platform == "coinmarketcap":
            return f"https://coinmarketcap.com/currencies/{local_slug}/"
        elif platform == "coingecko":
            return f"https://www.coingecko.com/en/coins/{local_slug}"

    @classmethod
    def new_listings(cls,db:DB = None) -> dict:
        with cls.with_db(db) as db:
            token_listings = {}
            results = db.get_all(
                f"""
                SELECT token,platform,added,local_slug
                FROM listings
                WHERE added > {time() - 60*60*24}
                ORDER BY added DESC
                """
            )
            for row in results:
                token = str(Address(row[0]))
                if token not in token_listings:
                    token_listings[token] = []
                token_listings[token].append(cls._from_row(row))
            return token_listings

    @classmethod
    def get_listings(cls, token_address: Address):
        token_address = str(Address(token_address))
        with DB("tokens") as db:
            rows = db.get_all(
                f"SELECT token,platform,added,local_slug FROM listings WHERE token = {db.placeholder(1)}",
                [token_address]
            )
            return [cls._from_row(row) for row in rows]
    
    @classmethod
    def from_slug(cls,listings:list, db:DB = None):
        conds = []
        params = []
        print(listings[0])
        for platform,name in listings:
            params.append(platform)
            params.append(name)
            conds.append(f"(platform = %s AND local_slug = %s)")
        with cls.with_db(db) as db:
            sql = f"""
            SELECT
                token,
                platform,
                added,
                local_slug
            FROM listings
            WHERE ({' OR '.join(conds)})
            """
            return [cls._from_row(row) for row in db.get_all(sql,params)]
