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
    
    @classmethod
    def get_filtered(cls,filters:dict = {},limit:int = None):
        query = cls._build(**filters)
        query += f"""
        ORDER BY created DESC NULLS LAST
        {cls.limit_cond(limit)}
        """
        with DB("tokens") as db:
            rows = db.get_all(query)
            return [cls._from_row(row) for row in rows]

    @classmethod
    def busd_to_wbnb(self,busd_value):
        return 1.5

    @classmethod
    def _build(
        cls,
        only_source_verified=False,
        min_liquidity_500 = False
    ):
        conds = []
        with_prices = False

        if only_source_verified:
            conds.append("source_verified = TRUE")
        if min_liquidity_500:
            with_prices = True
            conds.append(f"token_prices.liquidity >= {cls.busd_to_wbnb(500)}")
        cond_str = "" if len(conds) < 1 else f"WHERE {' AND '.join(conds)}"

        return cls._build_query(cond_str,with_prices=with_prices)
