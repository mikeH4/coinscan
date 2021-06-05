from core.Holders.Holders import Holders
from core.Token.Token import Token

class ViewableHolders(Holders):
    keys_rename = dict(
        holder=[None,str],
        holder_tag=["tag"],
    )
    added_attr = dict(
        holding=lambda token,holding,**attrs : float(holding)/float(token.total_supply)
    )

    @staticmethod
    def filter_top_holders(holders):
        if len(holders) < 1:
            return []
        top_holdings = [holders[0]]
        for i,holder in enumerate(holders[1:]):
            # i+1-1
            last_perc = holders[i].holding*100
            perc = holder.holding*100
            if (last_perc - perc) < 15 or perc >= 5:
                top_holdings.append(holder)
            else:
                break

        return top_holdings

    def __init__(self, **attrs) -> None:
        for key,new_key_tuple in self.keys_rename.items():
            new_key = new_key_tuple[0]
            new_key = key if new_key is None else new_key
            val = attrs[key]
            if len(new_key_tuple) > 1:
                val = new_key_tuple[1](val)
            setattr(self,new_key,val)
        
        attrs["token"] = Token.get(attrs["contract"])
        for key,get_func in self.added_attr.items():
            setattr(self,key,get_func(**attrs))