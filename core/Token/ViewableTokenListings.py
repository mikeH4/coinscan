from typing import Optional
from library.postgres import DB
from core.types.AddressHash import AddressHash, Validate
from core.types.db_types import ChainEnum, PlatformsEnum
from library.BaseModel import BaseModel

class ViewableTokenListings(BaseModel):
    chain: ChainEnum
    token_address: AddressHash
    platform: PlatformsEnum
    platform_id: str
    added: int

    def __init__(self,
        chain: ChainEnum,
        token_address: AddressHash,
        platform: PlatformsEnum,
        platform_id: str,
        added: int,
    ): pass

    @staticmethod
    def _build_query(where: str = ""):
        query = f"""
        SELECT
            address.chain AS chain,
            address.address AS address,
            token_listings.platform AS platform,
            token_listings.local_slug AS platform_id,
            token_listings.added AS added
        FROM token_listings
        JOIN address ON address.id = token_listings.id
        {where}
        """
        return query

    @classmethod
    def for_token(cls, chain: ChainEnum, address: AddressHash, *, db: DB = None):
        chain, address = Validate(chain, address)
        with cls.with_db(db) as db:
            query = cls._build_query(f"""
            WHERE address.chain = {db.placeholder(1)}
            AND address.address = {db.placeholder(1)}
            """)
            return [
                cls._from_row(row)
                for row
                in db.get_all(query, [chain, address])
            ]

    @classmethod
    def new_listings(cls, *, db: DB = None):
        with cls.with_db(db) as db:
            query = cls._build_query(f"""
            ORDER BY token_listings.added DESC
            """)
            return [
                cls._from_row(row)
                for row
                in db.get_all(query)
            ]

    @classmethod
    def unlisted(cls,
        chain: Optional[ChainEnum] = None,
        limit: Optional[int] = None,
        db: Optional[DB] = None
    ):
        chain_cond: str = "" if chain is None else f"AND address.chain = {DB.placeholder(1)}"
        chain_params = [] if chain is None else [chain]
        with cls.with_db(db) as db:
            query = cls._build_query(f"""
            LEFT JOIN token_meta ON token_listings.id = token_meta.id
            WHERE token_meta.id IS NULL
            {chain_cond}
            {cls.limit_cond(limit)}
            """,chain_params)
            return [cls._from_row(row) for row in db.get_all(query)]