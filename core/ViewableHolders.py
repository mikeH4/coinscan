from core.Holders import Holders

class ViewableHolders(Holders):
    keys_rename = dict(
        holder=[None,str],
        holder_tag=["tag"],
        holding=[None],
    )
    added_attr = dict()

    def __init__(self, **attrs) -> None:
        for key,new_key_tuple in self.keys_rename.items():
            new_key = new_key_tuple[0]
            new_key = key if new_key is None else new_key
            val = attrs[key]
            if len(new_key_tuple) > 1:
                val = new_key_tuple[1](val,**attrs)
            setattr(self,new_key,val)
        
        for key,get_func in self.added_attr.items():
            setattr(self,key,get_func(**attrs))