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
    def _build_query(where:str = "",with_liquidity = False):
        query = f"""
        SELECT
            tokens.address,
            tokens.name,
            tokens.symbol,
            token_meta.source_verified AS source_verified,
            token_meta.holders AS holders,
            token_meta.block_time AS created,
            listings.listings AS listings,
            address_labels.labels AS labels
        FROM tokens
        LEFT JOIN (
            SELECT
                listings.token,
                string_agg(listings.platform, ',') AS listings
            FROM listings
            GROUP BY listings.token
        ) as listings ON tokens.address = listings.token
        LEFT JOIN token_meta ON tokens.address = token_meta.address
        LEFT JOIN (
            SELECT
                address_labels.address,
                string_agg(address_labels.label, ',') AS labels
            FROM address_labels
            GROUP BY address_labels.address
        ) as address_labels ON token_meta.creator = address_labels.address
        {'' if not with_liquidity else '''
        LEFT JOIN (
            SELECT
                token,
                bnb_reserves * (
                    SELECT token_reserves/bnb_reserves
                    FROM liquidity_pairs
                    WHERE token = '0xe9e7cea3dedca5984780bafc599bd69add087d56'
                ) AS liquidity
            FROM liquidity_pairs
        ) as liquidity ON tokens.address = liquidity.token
        '''}
        {where}
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
    def get_latest(cls,limit=100,where_cond = "",with_liquidity=False):
        limit_cond = cls.limit_cond(limit)
        query = cls._build_query(where_cond,with_liquidity=with_liquidity)
        query += f"""
        ORDER BY created DESC NULLS LAST
        {limit_cond}
        """
        with DB("tokens") as db:
            rows = db.get_all(query)
            print(rows[0])
            return [cls._from_row(row) for row in rows]