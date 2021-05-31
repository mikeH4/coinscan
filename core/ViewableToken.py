from core.Listing import Listing
from core.Holders import Holders
import timeago
from datetime import datetime
from core.Token import Token
from core.CoreToken import CoreToken
from library.num import human_format

class ViewableToken(Token):
    keys_rename = dict(
        name=[None],
        symbol=[None],
        address=[None],
        block_time=[
            "timestamp",
            lambda timestamp : None if timestamp == 0 else timeago.format(datetime.fromtimestamp(timestamp))
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
        holders=[None,human_format],
    )
    added_attr = dict(
        listings=lambda address,**attrs : [listing.platform for listing in Listing.get_listings(address)]
    )

    def __init__(self, **attrs) -> None:
        for key,new_key_tuple in self.keys_rename.items():
            new_key = new_key_tuple[0]
            new_key = key if new_key is None else new_key
            val = attrs[key]
            if len(new_key_tuple) > 1:
                val = new_key_tuple[1](val)
            setattr(self,new_key,val)
        
        for key,get_func in self.added_attr.items():
            setattr(self,key,get_func(**attrs))