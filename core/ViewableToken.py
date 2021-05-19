from core.Holders import Holders
import timeago
from datetime import datetime
from core.Token import Token
from library.num import human_format

def get_largest_holder(self):
    holders = Holders.get_by_address(self.address)
    if len(holders) < 1:
        return "No holders"
    return holders[0].alert()


class ViewableToken(Token):
    keys_rename = dict(
        name=[None],
        symbol=[None],
        address=[None],
        block_time=[
            "timestamp",
            lambda timestamp : timeago.format(datetime.fromtimestamp(timestamp))
        ],
        description=[None],
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
        not_pausable=["ts_not_pausable",bool],
    )
    added_attr = dict(
        largest_holder= get_largest_holder
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
        
        for key,get_func in self.added_attr.items():
            setattr(self,key,get_func(self))