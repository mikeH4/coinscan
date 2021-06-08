from core.types.Address import Address, BlockOrTransactionHash
from library.postgres import DB
from library.BaseModel import BaseModel

class ViewableToken(BaseModel):
    def __init__(self,
        address:str,
        name:str,
        symbol:str,

        source_verified:bool,
        holders:int,
        created:int,

        listings:str,
        creator_labels:str,
    ) -> None:
        pass

    @staticmethod
    def _build_query(where:str = ""):
        query = f"""
        SELECT
            tokens.address,
            tokens.name,
            tokens.symbol,
            bool_or(token_meta.source_verified) AS source_verified,
            min(token_meta.holders) AS holders,
            min(token_meta.block_time) AS created,
            string_agg(listings.platform, ',') AS listings,
            string_agg(address_labels.label, ',') AS creator_labels
        FROM tokens
        LEFT JOIN listings ON tokens.address = listings.token
        LEFT JOIN token_meta ON tokens.address = token_meta.address
        LEFT JOIN address_labels ON token_meta.creator = address_labels.address
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
        ORDER BY created DESC NULLS LAST
        {limit_cond}
        """
        with DB("tokens") as db:
            rows = db.get_all(query)
            print(rows[0])
            return [cls._from_row(row) for row in rows]