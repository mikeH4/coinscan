from library.BaseModel import BaseModel
from core.types.Address import Address
from library.postgres import DB

class ViewableHolders(BaseModel):
    keys_rename = dict(
    )
    added_attr = {}

    def __init__(self, 
        holder:str,
        holding:float,
        is_contract:bool,
        holder_tag:str,
    ) -> None: pass    

    @classmethod
    def top(cls, address: Address, limit=10):
        address = str(Address(address))
        limit_cond = cls.limit_cond(limit)
        with DB("tokens") as db:
            query = f"""
            SELECT
                holders.holder,
                holders.holding,
                address_info.is_contract,
                address_info.bscscan_tag
            FROM holders
            JOIN address_info ON address_info.address = holders.holder
            WHERE contract = {db.placeholder(1)}
            ORDER BY holding DESC {limit_cond}
            """
            tokens = db.get_all(query,[address])
            return [cls._from_row(token) for token in tokens]