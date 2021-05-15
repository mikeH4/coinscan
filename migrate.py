from library.db import DB
from core.ViewableToken import ViewableToken

keys = ", ".join(ViewableToken.keys)

db = DB("data/tokens.db")

db.query(f"INSERT INTO tokens_temp SELECT {keys} FROM tokens;")
db.conn.commit()

db.query("DROP TABLE tokens;")
db.conn.commit()

db.query("ALTER TABLE tokens_temp RENAME TO tokens;")
db.conn.commit()