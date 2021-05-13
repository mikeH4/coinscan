from core.Token import Token

class ViewableToken(Token):
    keys_rename = dict(
        name=None,
        symbol=None,
        address=None,
        block_time="timestamp",
        total_supply=None,
        source_verified=None,
        rating="bscheck_rating",
        honeypot_check="bscheck_honeypot",
        owner_renounced="bscheck_renounced",
        lp_check="bscheck_lp_check",
        top_holders_check="bscheck_top_holders",
        no_older_tokens="no_prior_similar",
        not_proxy=None,
        not_pausable=None
    )

    @classmethod
    def _from_row(cls,row):
        attrs = {}
        for i,key in enumerate(cls.keys):
            if key not in cls.keys_rename:
                continue
            new_key = cls.keys_rename[key]
            new_key = key if new_key is None else new_key
            attrs[new_key] = row[i]
        return cls(**attrs)
    
    def __init__(self, **attrs) -> None:
        for key,new_key in self.keys_rename.items():
            new_key = key if new_key is None else new_key
            setattr(self,new_key,attrs[new_key])