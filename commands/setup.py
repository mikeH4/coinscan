from core.Token.CoreToken import CoreToken
from core.Holders.Holders import Holders
from core.misc.Proxies import Proxies
from core.misc.TokenRequest import TokenRequest
from core.misc.Listing import Listing
from library.postgres import DB

db = DB("tokens")

for _class in [CoreToken,Holders,Proxies,TokenRequest,Listing]:
    print(_class)

    if input(f"Create table '{_class.table}'?").lower() != "y":
        continue

    db.query(_class._db_create())
    db.conn.commit()