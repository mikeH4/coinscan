from library.BaseModel import BaseModel
from core.types.Address import Address

class TokenSnifferRating(BaseModel):
    table = "tokensniffer_rating"
    primary = ["address"]

    def __init__(self,
        address:Address,
        deployed:int,
        first_seen:int,
        source_md5:str,
        similar_count:int,
        similar_viewable:int,
        no_older_tokens:bool,
        not_proxy:bool,
        not_pausable:bool,
        updated:int
    ) -> None: pass