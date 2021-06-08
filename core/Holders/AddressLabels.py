from library.BaseModel import BaseModel
from core.types.Address import Address

class AddressLabels(BaseModel):
    table = "address_labels"
    primary = ["address","label"]

    def __init__(self,
        address:Address,
        label:str,
        added:int
    ) -> None: pass