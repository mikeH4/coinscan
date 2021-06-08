from core.Holders.Holders import Holders
from core.Token.TokenMeta import TokenMeta

class ViewableHolders(Holders):
    keys_rename = dict(
        holder=[None,str],
        holding=["amount"],
        holder_tag=["tag"],
    )
    added_attr = dict(
        holding=lambda token_meta,holding,**attrs : 0 if token_meta.total_supply is None else float(holding)/float(token_meta.total_supply)
    )

    def __init__(self, **attrs) -> None:
        for key,new_key_tuple in self.keys_rename.items():
            new_key = new_key_tuple[0]
            new_key = key if new_key is None else new_key
            val = attrs[key]
            if len(new_key_tuple) > 1:
                val = new_key_tuple[1](val)
            setattr(self,new_key,val)
        
        attrs["token_meta"] = TokenMeta.get(attrs["contract"])
        
        for key,get_func in self.added_attr.items():
            setattr(self,key,get_func(**attrs))