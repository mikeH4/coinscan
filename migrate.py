from core.TokenModel import TokenModel
from core.CoreToken import CoreToken
from library.postgres import DB

tk = TokenModel(CoreToken)
print("New Columns:",tk.new_cols)

db = DB("tokens")
db.query(tk.recreate())
db.conn.commit()