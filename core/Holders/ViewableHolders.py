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
        with DB() as db:
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

            for row in rows:
                holding,liquidity = [
                    row[1] or 0,
                    row[2] or 0,
                ]
                max_liquidity = liquidity if liquidity > max_liquidity else max_liquidity
                max_holding = holding if holding > max_holding else max_holding

            max_keep_holding = max_holding/100
            max_keep_liquidity = max_liquidity/100

            tokens = []
            for row in rows:
                # == would work the same
                if limit is not None and len(tokens) >= limit:
                    break
                if (row[1] or 0) < max_keep_holding and (row[2] or 0) < max_keep_liquidity:
                    continue
                tokens.append(cls._from_row(row))

            return tokens

    def get_tokens(wallet: Address):
        wallet = str(Address(wallet))
        sql = f"""
        SELECT
            holders.holding,
            token_info.address as token_address,
            token_info.name as token_name,
            token_info.symbol as token_symbol,
            pair_of_info.address as pair_of_address,
            pair_of_info.name as pair_of_name,
            pair_of_info.symbol as pair_of_symbol
        FROM holders
        LEFT JOIN pairs ON pairs.pair = holders.contract
        LEFT JOIN tokens AS token_info ON token_info.address = holders.contract
        LEFT JOIN tokens AS pair_of_info ON pair_of_info.address = pairs.token
        WHERE holders.holder = {DB.placeholder(1)}
        ORDER BY holders.holding DESC
        LIMIT 50
        """
        with DB() as db:
            res = db.get_all(sql,[wallet])
            ret = {}
            for row in res:
                holding = row[0]
                
                if row[4] is None:
                    is_liquidity = False
                    token,name,symbol = row[1:4]
                else:
                    is_liquidity = True
                    token,name,symbol = row[4:]

                if token is None:
                    continue
                if token not in ret:
                    ret[token] = dict(
                        address=token,
                        name=name,
                        symbol=symbol,
                        amount=None,
                        liquidity=None
                    )
                
                if is_liquidity:
                    ret[token]["liquidity"] = holding
                else:
                    ret[token]["amount"] = holding
        
            return list(ret.values())