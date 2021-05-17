from library.sqlite import DB
from core.Token import Token

db = DB("data/tokens.db")

rows = db.get_all("SELECT * FROM tokens")
for row in rows:
    kwargs = {key:row[i] for i,key in enumerate(Token.keys)}
    Token.insert_or_update(Token(**kwargs),db)

db.conn.commit()