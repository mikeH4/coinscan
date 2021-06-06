from core.types.Address import Address
from library.postgres import DB
from library.BaseModel import BaseModel

class ViewableToken(BaseModel):
    def __init__(self,
        address:Address,
        name:str,
        symbol:str,
        
        listings:str,

        source_verified:bool,
        block_time:int,
        holders:int,

        bscheck_rating:str,
        honeypot_check:bool,
        owner_renounced:bool,
        dev_liquidity_check:bool,
        lp_check:bool,
        top_holders_check:bool,

        no_older_tokens:bool,
        not_proxy:bool,
        not_pausable:bool
    ) -> None:
        pass

        
    
    @classmethod
    def get(cls,address:Address):
        address = str(Address(address))
        query = """
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
        WHERE tokens.address = %s
        GROUP BY tokens.address
        """
        with DB("tokens") as db:
            return cls._from_row(db.get(query,[address]))

    @classmethod
    def search(cls,keyword,limit=10):
        limit_cond = cls.limit_cond(limit)
        lkey = keyword.lower()
        placeholder = DB.placeholder(1)
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
        WHERE tokens.address = {placeholder}
        OR LOWER(tokens.symbol) LIKE {placeholder}
        OR LOWER(tokens.name) LIKE {placeholder}
        GROUP BY tokens.address
        {limit_cond}
        """
        with DB("tokens") as db:
            rows = db.get_all(query,[keyword,*[f"%{lkey}%"] * 2])
            return [cls._from_row(row) for row in rows]