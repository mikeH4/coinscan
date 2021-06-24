from core.Token.ViewableToken import ViewableToken
from library.postgres import DB

class Query(ViewableToken):
    @classmethod
    def trending(cls,db:DB = None):
        with cls.with_db(db) as db:
            db.get_all("""
            SELECT
                token,
                (
                    ( (wbnb_liquidity_new/liquidity_new) / (wbnb_liquidity_old/liquidity_old) ) - 1
                ) * 100 AS price_change,
                liquidity_new
            FROM liquidity_change
            WHERE liquidity_old != 0
            AND wbnb_liquidity_new >= 0.5
            ORDER BY price_change DESC
            LIMIT 100
            """)