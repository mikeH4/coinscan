from core.TokenModel import TokenModel
from core.CoreToken import CoreToken
from library.postgres import DB

tk = TokenModel(CoreToken)
print("New Columns:",tk.new_cols)

if input("Sure you want to overwrite?").lower() != "y":
    exit()

db = DB("tokens")
db.query(tk.recreate())
db.conn.commit()