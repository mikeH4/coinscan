from core.types.db_types import ChainEnum
from core.sources.ScannerApi import ScannerApi
from core.Token.ViewableToken import ViewableToken
from library.database.postgres import DB
from library.Cache import Cache
from itertools import combinations

class Query(ViewableToken):
    @classmethod
    def get_filtered(cls,
        filters: dict[str,bool] = {},
        limit: int = 100
    ):
        query = cls._build(**filters)
        query += f"""
        ORDER BY created DESC NULLS LAST
        {cls.limit_cond(limit)}
        """
        with DB() as db:
            rows = db.get_all(query)
            return [cls._from_row(row) for row in rows]

    @staticmethod
    @Cache.wrap(("busd_value",),cache_for=5*60)
    def busd_to_wbnb(busd_value: float):
        return busd_value*ScannerApi().busd(ChainEnum("bsc"))["wbnb_for_1_busd"]

    @classmethod
    def _build(
        cls,
        only_source_verified: bool = False,
        min_liquidity_500: bool = False
    ):
        conds = []
        if only_source_verified:
            conds.append("source_verified = TRUE")
        if min_liquidity_500:
            conds.append(f"token_stats.liquidity >= {Query.busd_to_wbnb(busd_value=500)}")
        cond_str = "" if len(conds) < 1 else f"WHERE {' AND '.join(conds)}"

        return cls._build_query(cond_str)

    @classmethod
    def get_frequent_addresses(cls, limit: int = 100):
        filters = (
            "only_source_verified",
            "min_liquidity_500"
        )
        addresses = []
        for l in range(len(filters)+1):
            for posb in combinations(filters,l):
                f = {filter:True for filter in posb}
                addresses += cls.get_filtered(f,limit=limit)
        return list(set(addresses))