from core.types.db_types import ChainEnum, bigint
from library.database.postgres import DB
from library.database.BaseModel import BaseModel
from core.types.AddressHash import AddressHash, Validate

class ViewableWalletMeta(BaseModel):
    def __init__(self,
        chain: ChainEnum,
        wallet_address: AddressHash,
        is_contract: bool,
        holder_tag: str,
    ) -> None: pass

    @classmethod
    def get(cls, chain: ChainEnum, wallet_address: AddressHash):
        chain, wallet_address = Validate(chain, wallet_address)
        with DB() as db:
            row = db.get("""
            SELECT
                address.chain AS chain,
                address.address AS address,
                wallet_meta.is_contract AS is_contract,
                wallet_meta.bscscan_tag AS holder_tag
            FROM wallet_meta
            JOIN address ON address.id = wallet_meta.id
            WHERE address.chain = %s
            AND address.address = %s
            """,
            [chain,wallet_address])
            if row is None: return None
            
            return cls._from_row(row)
