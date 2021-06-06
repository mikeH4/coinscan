from core.types.Address import Address
from library.postgres import DB
from library.BaseModel import BaseModel

class ViewableToken(BaseModel):
    def __init__(self,
        address:Address,
        name:str,
        symbol:str,

        source_verified:bool,
        block_time:int,
        holders:int,

        listings:str,
    ) -> None:
        pass

    @staticmethod
    def _build_query(where:str):
        query = f"""
        SELECT
            tokens.address,
            tokens.name,
            tokens.symbol,
            string_agg(listings.platform, ',') AS listings,
            token_meta.source_verified AS source_verified,
            token_meta.holders AS holders,
            token_meta.block_time AS block_time,
        FROM tokens
        JOIN listings ON tokens.address = listings.token
        JOIN token_meta ON tokens.address = token_meta.address
        {where}
        GROUP BY tokens.address
        """
        return query

    
    @classmethod
    def get(cls,address:Address):
        address = str(Address(address))
        query = cls._build_query(f"WHERE tokens.address = {DB.placeholder(1)}")
        with DB("tokens") as db:
            return cls._from_row(db.get(query,[address]))

    @classmethod
    def search(cls,keyword,limit=10):
        limit_cond = cls.limit_cond(limit)
        lkey = keyword.lower()
        placeholder = DB.placeholder(1)
        query = cls._build_query(f"""
        WHERE tokens.address = {placeholder}
        OR LOWER(tokens.symbol) LIKE {placeholder}
        OR LOWER(tokens.name) LIKE {placeholder}
        """)
        query += limit_cond
        with DB("tokens") as db:
            rows = db.get_all(query,[keyword,*[f"%{lkey}%"] * 2])
            return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_latest(cls,limit=100):
        limit_cond = cls.limit_cond(limit)
        query = cls._build_query()
        query += f"""
        ORDER BY token_meta.block_time DESC
        {limit_cond}
        """
        with DB("tokens") as db:
            rows = db.get_all(query)
            return [cls._from_row(row) for row in rows]