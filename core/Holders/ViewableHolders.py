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
        with DB("tokens") as db:
            query = f"""
            SELECT 
                CASE WHEN holders.holder IS NOT NULL
                    THEN holders.holder ELSE pair_holders.holder
                END AS holder,
                holding,
                liquidity,
                address_info.is_contract,
                address_info.bscscan_tag
            FROM (
                SELECT
                    holders.holder,
                    holding
                FROM holders
                WHERE holders.contract = {db.placeholder(1)}
            ) AS holders
            FULL OUTER JOIN (
                SELECT
                    holder,
                    holding AS liquidity
                FROM holders
                JOIN pairs ON pairs.pair = holders.contract
                WHERE pairs.token = {db.placeholder(1)}
                AND holders.holder != '0x0000000000000000000000000000000000000000'
            ) AS pair_holders ON pair_holders.holder = holders.holder
            JOIN address_info ON address_info.address = (
                CASE WHEN holders.holder IS NOT NULL
                    THEN holders.holder ELSE pair_holders.holder
                END
            )
            
            ORDER BY
                liquidity DESC NULLS LAST,
                holding DESC NULLS LAST
            """
            rows = db.get_all(query,[address]*2)
            max_liquidity = 0
            max_holding = 0
            partially_filtered = 

            for row in rows:
                holding,liquidity = row[1:2]
                # Check here to ensure less loops in second for
                if max_holding/100 > holding: continue
                if max_liquidity/100 > liquidity: continue

                max_liquidity = liquidity if liquidity > max_liquidity else max_liquidity
                max_holding = holding if holding > max_holding else max_holding




            return [cls._from_row(token) for token in tokens]