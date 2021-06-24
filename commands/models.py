from library.BaseModel import BaseModel

from core.Token.Token import Token
from core.Token.TokenMeta import TokenMeta
from core.Token.BSCheckRating import BSCheckRating
from core.Token.TokenSnifferRating import TokenSnifferRating

from core.Holders.Holders import Holders
from core.Holders.AddressLabels import AddressLabels
from library.Proxies import Proxies
from core.misc.TokenRequest import TokenRequest
from core.misc.Listing import Listing
from core.misc.LiquidityPairs import LiquidityPairs
from core.misc.TokenPrices import TokenPrices

models = [
    cls
    for cls in BaseModel.__subclasses__()
    if cls.table is not None
]

db_name = "tokens"