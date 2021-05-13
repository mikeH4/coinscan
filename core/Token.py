from datetime import datetime
from core.Address import Address
from core.CoreToken import CoreToken

class Token(CoreToken):
    @classmethod
    def from_row(cls,row):
        token = cls()
        token = do_some_crap(row)
        return token

    @staticmethod
    def to_row(cls, row):
        return {}


    @classmethod
    def get(cls, address):
        token = db.get(address)
        if token is None:
            return None
        return cls.from_row(token)