from library.database.postgres import DB
from typing import Optional
from core.types.db_types import ChainEnum, numeric
from core.types.AddressHash import AddressHash
from core.sources.BscScan import ChainScan
from core.Address import Address
from core.StateTime import StateTime
from core.Token.TokenStats import TokenStats

def pull_and_update(*,
    chain: ChainEnum,
    token_address: AddressHash,
    pair_address: Optional[AddressHash] = None,
    db: Optional[DB] = None
):
    ret = ChainScan(chain).holders(token_address if pair_address is None else pair_address)
    token_id = Address._confirm(chain=chain,address=token_address)
    StateTime.upsert(
        key="wallet_supply" if pair_address is None else "wallet_liquidity",
        id=token_id,
        db=db
    )
    if ret is None: return

    total, top = ret
    TokenStats(
        id=token_id,
        holders=numeric(total)
    ).insert_or_update(
        chain=chain,
        token_address=token_address,
        dont_update=["total_supply","circulating","price_change","liquidity"],
        db=db
    )

    for wallet_address, wallet_meta, wallet_holding in top:
        wallet_holding.token_id = token_id
        
        dont_update = ["wallet_id","token_id","supply"]
        if pair_address is not None:
            wallet_holding.liquidity = wallet_holding.supply
            wallet_holding.supply = numeric(0)
            dont_update = ["wallet_id","token_id","liquidity"]
        
        print(f"Inserted wallet {wallet_address} for {token_address}")
        wallet_id = wallet_holding.insert_with_wallet_upsert(
            chain=chain,
            wallet_address=wallet_address,
            dont_update=dont_update,
            db=db
        )

        wallet_meta.id = wallet_id
        wallet_meta._upsert_by_id(db=db)
