from library.BaseModel import BaseModel

from core.Token.Token import Token
from core.Token.TokenMeta import TokenMeta

from core.Holders.Holders import Holders
from core.Holders.AddressLabels import AddressLabels
from core.misc.Listing import Listing
from core.misc.TokenPrices import TokenPrices
from core.misc.Pairs import Pairs

models = [
    cls
    for cls in BaseModel.__subclasses__()
    if cls.table is not None
]

db_name = "tokens"