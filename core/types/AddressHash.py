import re
from core.types.db_types import ChainEnum

class AddressHash(str):
    regex = "0x[a-fA-F0-9]{40}"
    def __new__(cls, address: str):
        address = str(address).lower()
        if re.fullmatch(cls.regex,address) is None:
            raise TypeError("AddressHash is invalid")
        return super(AddressHash, cls).__new__(cls, address)

    def __repr__(self) -> str:
        return f"<Address: {self}>"

def Validate(chain: ChainEnum, address: AddressHash):
    return (ChainEnum(chain), AddressHash(address))

class BlockOrTransactionHash(str):
    regex = "0x[a-fA-F0-9]{64}"
    def __new__(cls, address: str):
        address = str(address).lower()
        if re.fullmatch(cls.regex,address) is None:
            raise TypeError("BlockOrTransactionHash is invalid")
        return super(BlockOrTransactionHash, cls).__new__(cls, address)

    def __repr__(self) -> str:
        return f"<BlockOrTransactionHash: {self}>"