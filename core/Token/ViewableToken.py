from core.types.db_types import ChainEnum, numeric
from library.postgres import DB
from core.types.AddressHash import AddressHash, Validate
from library.BaseModel import BaseModel

class ViewableToken(BaseModel):
    def __init__(self,
        chain: ChainEnum,
        address: AddressHash,
        name: str,
        symbol: str,
        source_verified: bool,
        created: int,
        holders: numeric,
        listing: str
    ): pass

    @classmethod
    def get(cls, chain: ChainEnum, address: AddressHash):
        chain, address = Validate(chain, address)
        query = cls._build_query(
            f"WHERE address.chain = {DB.placeholder(1)} AND address.address = {DB.placeholder(1)}"
        )
        with DB() as db:
            row = db.get(query, [chain, address])
            if row is None: return None
            return cls._from_row(row)

    @staticmethod
    def _build_query(where: str = ""):
        query = f"""
        SELECT
            address.chain AS chain,
            address.address AS address,
            token_meta.name AS name,
            token_meta.symbol AS symbol,
            token_meta.source_verified AS source_verified,
            token_meta.created_time AS created,
            token_stats.holders AS holders,
            token_listings.stringified AS listings
        FROM token_meta
        JOIN address ON token_meta.id = address.id
        LEFT JOIN token_stats ON token_meta.id = token_stats.id
        LEFT JOIN (
            SELECT
                token_listings.id,
                string_agg(token_listings.platform::text, ',') AS stringified
            FROM token_listings
            GROUP BY token_listings.id
        ) AS token_listings ON token_meta.id = token_listings.id
        {where}
        """
        return query

    @classmethod
    def search(cls, keyword: str):
        keyword = keyword.lower()
        query = cls._build_query(f"""
        WHERE address.address = {DB.placeholder(1)}
        OR LOWER(token_meta.name) LIKE {DB.placeholder(1)}
        OR LOWER(token_meta.symbol) LIKE {DB.placeholder(1)}
        ORDER BY token_stats.liquidity DESC NULLS LAST
        """)
        with DB() as db:
            rows = db.get_all(query,[keyword,*[f"%{keyword}%"] * 2])
            return [cls._from_row(row) for row in rows]