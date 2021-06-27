from library.BaseModel import BaseModel
from core.types.Address import Address
from library.postgres import DB

class ViewableHolders(BaseModel):
    def __init__(self, 
        holder:str,
        amount:float,
        liquidity:float,
        is_contract:bool,
        holder_tag:str,
    ) -> None: pass    

    @classmethod
    def top(cls, address: Address, limit=10):
        address = str(Address(address))
        limit_cond = cls.limit_cond(limit)
        with DB("tokens") as db:
            query = f"""
            SELECT holders.holder,
                holders.holding,
                pair_holders.holding AS liquidity,
                address_info.is_contract,
                address_info.bscscan_tag
            FROM holders
            JOIN address_info ON address_info.address = holders.holder
            LEFT JOIN pairs ON pairs.token = holders.contract

            LEFT JOIN holders AS pair_holders ON pairs.pair = pair_holders.contract
            WHERE holders.contract = {db.placeholder(1)}

            AND pair_holders.holder != '0x0000000000000000000000000000000000000000'

            ORDER BY
                pair_holders.holding DESC NULLS LAST,
                holders.holding DESC NULLS LAST

            {limit_cond}
            """
            tokens = db.get_all(query,[address])
            return [cls._from_row(token) for token in tokens]