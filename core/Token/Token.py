from core.types.Address import Address
from core.misc.Listing import Listing
from core.Token.CoreToken import CoreToken
from library.postgres import DB

class Token(CoreToken):
    @staticmethod
    def _get_latest_in_rows(limit=100,before=None):
        limit_cond = Token.limit_cond(limit)
        before_cond = Token.before_cond(before)

        with DB("tokens") as db:
            return db.get_all(f"SELECT * FROM tokens {before_cond} ORDER BY block_time DESC {limit_cond}")

    @classmethod
    def get_latest(cls, limit=100, before=None):
        rows = cls._get_latest_in_rows(limit=limit, before=before)
        addresses = [row[0] for row in rows]
        Listing.cache_listings(addresses)
        return [cls._from_row(row) for row in rows]

    @classmethod
    def search(cls,keyword,limit=10):
        lkey = keyword.lower()
        limit_cond = ""
        if limit is not None:
            limit_cond = f"LIMIT {int(limit)}"
        with DB("tokens") as db:
            placeholder = db.placeholder(1)
            sql = f"""
            SELECT * FROM tokens
            WHERE
            address = {placeholder}
            OR LOWER(symbol) LIKE {placeholder}
            OR LOWER(name) LIKE {placeholder}
            {limit_cond}
            """
            rows = db.get_all(sql,[keyword,*[f"%{lkey}%"] * 2])
            addresses = [row[0] for row in rows]
            Listing.cache_listings(addresses)
            return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _get_these(cls, addresses):
        with DB("tokens") as db:
            placeholder = db.placeholder(len(addresses))
            sql = f"SELECT * FROM tokens WHERE address IN ({placeholder})"
            rows = db.get_all(sql,addresses)
            return [cls._from_row(row) for row in rows]

    @classmethod
    def get_newly_listed(cls):
        with DB("tokens") as db:
            return cls._get_these(Listing.new_listings())


    @classmethod
    def get(cls, address: Address):
        address = str(Address(address))
        with DB("tokens") as db:
            placeholder = db.placeholder(1)
            token = db.get(f"SELECT * FROM tokens WHERE address = {placeholder}",[address])
            if token is None:
                return None
            return cls._from_row(token)
        
    def insert_or_update(self,db:DB = None,dont_update:list=[],ignore=False):
        _db = db if db is not None else DB("tokens")

        _dict = self.dict()
        address = _dict["address"]
        _dict["address"] = str(_dict["address"])
        _db.insert(
            "tokens",
            _dict,
            replace_insert_on=["address"],
            commit=False,
            dont_update=dont_update,
            ignore_insert=ignore
        )
        print("Inserted:", address)

        if db is None:
            _db.close()