from core.CoreToken import CoreToken
from core.Holders import Holders
from core.Proxies import Proxies
from core.TokenRequest import TokenRequest
from core.Listing import Listing
from library.postgres import DB

db = DB("tokens")

for _class in [CoreToken,Holders,Proxies,TokenRequest,Listing]:
    print(_class)

    if input(f"Create table '{_class.table}'?").lower() != "y":
        continue

    db.query(_class._db_create())
    db.conn.commit()