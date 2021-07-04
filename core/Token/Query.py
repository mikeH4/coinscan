from core.sources.ScannerApi import ScannerApi
from core.Token.ViewableToken import ViewableToken
from library.postgres import DB
from core.Cache import Cache
from itertools import combinations

class Query(ViewableToken):
    @classmethod
    def get_filtered(cls,filters:dict = {},limit:int = 100):
        query = cls._build(**filters)
        query += f"""
        ORDER BY created DESC NULLS LAST
        {cls.limit_cond(limit)}
        """
        with DB("tokens") as db:
            rows = db.get_all(query)
            return [cls._from_row(row) for row in rows]

    @staticmethod
    @Cache.wrap(["busd_value"],cache_for=5*60)
    def busd_to_wbnb(busd_value):
        return busd_value*ScannerApi(limit_bypass=True).busd()["wbnb_for_1_busd"]

    @classmethod
    def _build(
        cls,
        only_source_verified=False,
        min_liquidity_500=False
    ):
        conds = []
        with_prices = False

        if only_source_verified:
            conds.append("source_verified = TRUE")
        if min_liquidity_500:
            with_prices = True
            conds.append(f"token_prices.liquidity >= {Query.busd_to_wbnb(busd_value=500)}")
        cond_str = "" if len(conds) < 1 else f"WHERE {' AND '.join(conds)}"

        return cls._build_query(cond_str,with_prices=with_prices)

    @classmethod
    def get_frequent_addresses(cls,limit=100):
        filters = (
            "only_source_verified",
            "min_liquidity_500"
        )
        addresses = []
        for l in range(len(filters)+1):
            for posb in combinations(filters,l):
                f = {filter:True for filter in posb}
                print(f)
                addresses += cls.get_filtered(f,limit=limit)
        return list(set(addresses))