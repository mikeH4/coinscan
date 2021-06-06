from library.postgres import DB
from library.BaseModel import BaseModel

# Models
from core.Token.Token import Token
from core.Token.TokenMeta import TokenMeta
from core.Token.BSCheckRating import BSCheckRating
from core.Token.TokenSnifferRating import TokenSnifferRating

from core.Holders.Holders import Holders
from library.Proxies import Proxies
from core.misc.TokenRequest import TokenRequest
from core.misc.Listing import Listing

with DB("tokens") as db:
    for _class in BaseModel.__subclasses__():
        if _class.table is None:
            continue
        print(_class)
        print("New Columns:",_class._db_new_cols())

        if input("Sure you want to overwrite?").lower() != "y":
            continue
        
        try:
            db.query(_class._db_recreate())
            db.conn.commit()
        except Exception as e:
            if input("Delete old temp table?").lower() == "y":
                db.rollback()
                db.query(f"DROP TABLE {_class.table}_temp;")
                db.query(_class._db_recreate())
                db.conn.commit()