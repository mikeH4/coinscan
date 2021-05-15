import timeago
from datetime import datetime
from core.Token import Token
from library.numbers import human_format

class ViewableToken(Token):
    keys_rename = dict(
        name=[None],
        symbol=[None],
        address=[None],
        block_time=[
            "timestamp",
            lambda timestamp : timeago.format(datetime.fromtimestamp(timestamp))
        ],
        total_supply=[None,human_format],
        source_verified=[None,bool],
        rating=["bscheck_rating",lambda rating : "unrated" if not rating else rating],
        honeypot_check=["bscheck_honeypot",bool],
        owner_renounced=["bscheck_renounced",bool],
        lp_check=["bscheck_lp_check",bool],
        top_holders_check=["bscheck_top_holders",bool],
        deployed=["ts_found",bool],
        no_older_tokens=["ts_no_prior_similar",bool],
        not_proxy=["ts_not_proxy",bool],
        not_pausable=["ts_not_pausable",bool]
    )

    @classmethod
    def _from_row(cls,row):
        attrs = {}
        for i,key in enumerate(cls.keys):
            if key not in cls.keys_rename:
                continue
            new_key = cls.keys_rename[key][0]
            new_key = key if new_key is None else new_key
            val = row[i]
            if len(cls.keys_rename[key]) > 1:
                val = cls.keys_rename[key][1](row[i])
            attrs[new_key] = val
        return cls(**attrs)
    
    def __init__(self, **attrs) -> None:
        for key,new_key in self.keys_rename.items():
            new_key = new_key[0]
            new_key = key if new_key is None else new_key
            setattr(self,new_key,attrs[new_key])