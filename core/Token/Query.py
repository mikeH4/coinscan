import itertools
from typing import Optional, Union
from core.types.db_types import ChainEnum
from core.sources.ScannerApi import ScannerApi
from core.Token.ViewableToken import ViewableToken
from library.database.postgres import DB
from library.Cache import Cache

class Query(ViewableToken):
    @classmethod
    def get_filtered(cls,
        filters: dict[str,Union[bool,Optional[ChainEnum]]] = {},
        limit: int = 100
    ):
        query = cls._build(**filters)
        query += f"""
        ORDER BY created DESC NULLS LAST
        {cls.limit_cond(limit)}
        """
        with DB() as db:
            rows = db.get_all(query)
            return [ViewableToken._from_row(row) for row in rows]

    @staticmethod
    @Cache.wrap(("busd_value",),cache_for=5*60)
    def busd_to_wbnb(busd_value: float):
        return busd_value*ScannerApi().busd(ChainEnum("bsc"))["wbnb_for_1_busd"]

    @classmethod
    def _build(
        cls,
        only_source_verified: bool = False,
        min_liquidity_500: bool = False,
        chain: Optional[ChainEnum] = ChainEnum("bsc")
    ):
        conds = []
        if only_source_verified:
            conds.append("source_verified = TRUE")
        if min_liquidity_500:
            conds.append(f"token_stats.liquidity >= {Query.busd_to_wbnb(busd_value=500)}")
        if chain is not None:
            chain = ChainEnum(chain)
            conds.append(f"address.chain = '{chain}'")

        cond_str = "" if len(conds) < 1 else f"WHERE {' AND '.join(conds)}"

        return cls._build_query(cond_str)
    
    @classmethod
    def _get_possibilities(cls, key: str):
        if key == "only_source_verified":
            return (True,False)
        if key == "min_liquidity_500":
            return (True,False)
        if key == "chain":
            return (None,"eth","bsc")
        raise Exception("key is invalid")

    @classmethod
    def get_frequent_tokens(cls, limit: int = 100):
        filters = (
            "only_source_verified",
            "min_liquidity_500",
            "chain"
        )
        filters_possibilities = []
        for filter in filters:
            this_filter_possib = []
            for filter_possib in cls._get_possibilities(filter):
                this_filter_possib.append((filter,filter_possib))
            filters_possibilities.append(this_filter_possib)

        tokens = []
        combos = itertools.product(*filters_possibilities)
        for args in combos:
            kwargs = {filter:value for filter,value in args}
            tokens += cls.get_filtered(kwargs,limit=limit)

        return list(set(tokens))
