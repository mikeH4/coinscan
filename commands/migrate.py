from library.sqlite import DB
from library.postgres import DB as _DB
from core.Token import Token

db = DB("data/tokens.db")
_db = _DB("tokens")

rows = db.get_all("SELECT * FROM tokens")
for row in rows:
    kwargs = {key:row[i] for i,key in enumerate(Token.keys)}
    Token.insert_or_update(Token(**kwargs),_db)

_db.close()