from core.Holders import Holders
import timeago
from datetime import datetime
from core.Token import Token
from core.CoreToken import CoreToken
from library.num import human_format

def get_largest_holder(**attrs):
    token = CoreToken(**attrs)
    holders = Holders.get_by_address(token.address)
    if len(holders) < 1:
        return "No holders"
    sply = token.total_supply
    top_holdings = [holders[0].holding]
    for i,holder in enumerate(holders[1:]):
        # i+1-1
        last_perc = holders[i].holding/sply*100
        perc = holder.holding/sply*100
        if last_perc - perc < 15:
            top_holdings.append(holder.holding)
        else:
            break

    grammar = f"{len(top_holdings)} own"
    if len(top_holdings) == 1:
        grammar = f"wallet owns"
    return f"Top {grammar} {round(sum(top_holdings)/sply*100,2)}% of supply"


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