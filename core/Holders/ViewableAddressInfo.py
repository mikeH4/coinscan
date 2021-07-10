from library.BaseModel import BaseModel
from core.types.Address import Address
from library.postgres import DB

class ViewableAddressInfo(BaseModel):
    def __init__(self, 
        holder:str,
        is_contract:bool,
        holder_tag:str
    ) -> None: pass    

    @classmethod
    def get(cls, address: Address):
        address = str(Address(address))
        with DB() as db:
            row = db.get("""
            SELECT
                address,is_contract,bscscan_tag
            FROM address_info
            WHERE address = %s""",
            [address])
            if row is None: return None
            return cls._from_row(row)