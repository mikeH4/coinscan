from library.postgres import DB
from library.BaseModel import BaseModel

# Models
from core.Token.Token import Token
from core.Token.TokenMeta import TokenMeta
from core.Token.BSCheckRating import BSCheckRating
from core.Token.TokenSnifferRating import TokenSnifferRating

from core.Holders.Holders import Holders
from core.misc.Proxies import Proxies
from core.misc.TokenRequest import TokenRequest
from core.misc.Listing import Listing

with DB("tokens") as db:
    for _class in BaseModel.__subclasses__():
        print(_class)

        if input(f"Create table '{_class.table}'?").lower() != "y":
            continue

        db.query(_class._db_create())
        db.conn.commit()