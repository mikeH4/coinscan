from core.Token.TokenMeta import TokenMeta
from core.types.AddressHash import AddressHash
from library.postgres import DB
from core.types.db_types import ChainEnum, bigint, enum, numeric
from library.BaseModel import BaseModel

class TokenStats(BaseModel):
    table = "token_stats"
    primary = ["id"]

    id: bigint
    total_supply: numeric
    circulating: numeric
    price_change: bigint
    holders: numeric
    liquidity: numeric

    def __init__(self,
        id: bigint,
        holders: numeric = None,
        total_supply: numeric = None,
        price_change: bigint = None,
        circulating: numeric = None,
        liquidity: numeric = None
    ): pass

    def _upsert_by_id(self,
        *,
        dont_update: list[str] = [],
        db: DB = None
    ):
        if self.id == 0: raise TypeError("id cannot be 0")
        with self.with_db(db) as db:
            return db.insert(
                self.table,
                self.dict(),
                replace_insert_on = ["id"],
                dont_update=dont_update
            )
    
    def insert_or_update(self,
        *,
        chain: ChainEnum,
        token_address: AddressHash,
        dont_update: list[str] = [],
        db: DB = None
    ):
        query, values = TokenMeta._prep_query(self,dont_update=dont_update) #type: ignore

        with self.with_db(db) as db:
            ret = db.get(query,[chain,token_address] + values)
            assert ret is not None
            self.id = bigint(ret[0])
        
        return self.id
    
    @classmethod
    def replace_price_data(cls, *,
        chain: ChainEnum,
        data: list[tuple[str, numeric, numeric, numeric]]
    ):
        if len(data) < 1: return
        with DB(auto_commit=True) as db:
            update_cmd = []
            null_cmd = []
            for key in ["price_change","circulating","liquidity"]:
                update_cmd.append(f"{key} = excluded.{key}")
                null_cmd.append(f"{key} = NULL")
        
            db.query(f"UPDATE token_stats SET {','.join(null_cmd)}")

            values = []
            params = []
            for address,_,_,_ in data:
                values.append(f"({DB.placeholder(2)})")
                params += [chain, AddressHash(address)]

            sql = f"""
            INSERT INTO address (chain, address)
            VALUES {','.join(values)}
            ON CONFLICT (chain, address)
            DO UPDATE SET address = address.address
            RETURNING id
            """
            res = db.get_all(sql,params)
        
            assert len(res) == len(data)

            values = []
            params = []
            for i,data_row in enumerate(data):
                address, price_change, circulating, liquidity = data_row
                id = bigint(res[i][0])
                values.append(f"({DB.placeholder(4)})")
                params += [id,price_change,circulating,liquidity]
            
            sql = f"""
            INSERT INTO token_stats (id, price_change, circulating, liquidity)
            VALUES {','.join(values)}
            ON CONFLICT (id)
            DO UPDATE SET {','.join(update_cmd)}
            """
            db.query(sql,params)