from core.sources.ScannerApi import ScannerApi
from core.Token.ViewableToken import ViewableToken
from library.postgres import DB
from core.Cache import Cache

class Query(ViewableToken):
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

    @Cache.wrap(["busd_value"],cache_for=5*60)
    @classmethod
    def busd_to_wbnb(self,busd_value):
        return busd_value*ScannerApi().busd()["wbnb_for_1_busd"]

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
