from time import time
from typing import Optional
from core.Wallets.ViewableWalletMeta import ViewableWalletMeta
from core.types.db_types import ChainEnum, enum, numeric
from core.types.AddressHash import AddressHash, Validate
from library.postgres import DB

TokenOrWallet = enum("wallet","token")

class ViewableWalletHoldings(ViewableWalletMeta):
    def __init__(self,
        chain: ChainEnum,
        address: AddressHash,
        is_contract: bool,
        holder_tag: str,
        token: AddressHash,
        supply: numeric,
        liquidity: numeric
    ) -> None: pass

    @staticmethod
    def _build_query(where: str = ""):
        return f"""
        SELECT
            wallet_address.chain AS chain,
            wallet_address.address AS wallet_address,
            wallet_meta.is_contract AS is_contract,
            wallet_meta.bscscan_tag AS holder_tag,
            token_address.address AS token_address,
            wallet_holdings.supply AS supply,
            wallet_holdings.liquidity AS liquidity
        FROM wallet_holdings
        JOIN address AS wallet_address ON wallet_holdings.wallet_id = wallet_address.id
        JOIN address AS token_address ON wallet_holdings.token_id = wallet_address.id
        JOIN wallet_meta ON wallet_holdings.wallet_id = wallet_meta.id
        {where}
        """
    
    @staticmethod
    def _order_by():
        return """
        ORDER BY
            wallet_holdings.liquidity DESC NULLS LAST,
            wallet_holdings.supply DESC NULLS LAST
        """

    @classmethod
    def _get_holdings(cls,
        chain: ChainEnum,
        address: AddressHash,
        type: TokenOrWallet,
        *,
        limit = 10
    ):
        type = TokenOrWallet(type)
        chain, address = Validate(chain, address)
        with DB() as db:
            query = cls._build_query(f"""
            WHERE {type}_address.chain = {db.placeholder(1)}
            AND {type}_address.address = {db.placeholder(1)}
            {cls._order_by()}
            """)
            rows = db.get_all(query,[chain, address])
            max_liquidity = 0
            max_supply = 0

            for row in rows:
                supply, liquidity = [
                    row[5] or 0,
                    row[6] or 0,
                ]
                max_liquidity = max(liquidity, max_liquidity)
                max_supply = max(supply, max_supply)

            max_keep_supply = max_supply/100
            max_keep_liquidity = max_liquidity/100

            wallets = []
            for row in rows:
                # == would work the same
                if limit is not None and len(wallets) >= limit:
                    break
                if (row[1] or 0) < max_keep_supply and (row[2] or 0) < max_keep_liquidity:
                    continue
                wallets.append(cls._from_row(row))

            return wallets
    
    @classmethod
    def not_updated(cls, *,
        before_hours: int = 24,
        db: Optional[DB] = None
    ):
        before_time = int(time() - before_hours*60*60)
        with cls.with_db(db) as db:
            query = cls._build_query(f"""
            JOIN state_time ON state_time.id = wallet_meta.id
            WHERE state_time.key IS NULL OR (
                state_time.id = {db.placeholder(1)}
                AND state_time.time > {before_time}
            )
            ORDER BY state_time.time DESC NULLS FIRST
            """)

            return [cls._from_row(row) for row in db.get_all(query)]